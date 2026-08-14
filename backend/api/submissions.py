"""Code submission, evaluation, and realtime result routes."""

from datetime import datetime, timezone
import json
import time

from flask import Blueprint, Response, request, stream_with_context

from backend.api.auth import token_required
from backend.db import db
from backend.rbac import error_response
from backend.services.code_executor import get_executor
from backend.services.submission_queue import enqueue_submission


submissions_bp = Blueprint("submissions", __name__)
_FINAL_STATES = {"accepted", "partial_accepted", "rejected", "error"}


def _staff_user(user: dict) -> bool:
    return user.get("role") in {"owner", "admin", "teacher"}


def _result_payload(results, user: dict):
    if _staff_user(user):
        return results or []
    visible = []
    for result in results or []:
        if result.get("is_hidden"):
            visible.append(
                {
                    key: value
                    for key, value in result.items()
                    if key not in {"input", "expected_output", "solution", "is_hidden"}
                }
            )
        else:
            visible.append(result)
    return visible


def _submission_access_allowed(submission: dict, current_user: dict) -> bool:
    return submission.get("user_id") == current_user.get("id") or _staff_user(current_user)


@submissions_bp.route("", methods=["POST"])
@token_required
def create_submission(current_user):
    """Submit code for asynchronous graded evaluation."""
    if current_user.get("role") != "student":
        return error_response("student_only", "Only students can submit code.", "Зөвхөн суралцагч код илгээх боломжтой.", 403)

    data = request.get_json(silent=True) or {}
    if "problem_id" not in data or not isinstance(data.get("code"), str) or not data["code"].strip():
        return error_response("validation_error", "Problem ID and non-empty code are required.", "Бодлогын ID болон хоосон биш код шаардлагатай.", 400)

    try:
        problem = db.get_problem(data["problem_id"])
        if not problem:
            return error_response("problem_not_found", "Problem not found.", "Бодлого олдсонгүй.", 404)
        language = str(data.get("language") or problem.get("language") or "python").lower()
        if language not in {"python", "javascript"}:
            return error_response("unsupported_language", "Unsupported programming language.", "Дэмжигдээгүй програмчлалын хэл.", 400)
        submission = db.create_submission(
            user_id=current_user["id"],
            problem_id=data["problem_id"],
            code=data["code"],
            assignment_id=data.get("assignment_id"),
            exam_id=data.get("exam_id"),
        )
        if not submission:
            return error_response("submission_create_failed", "Submission could not be created.", "Илгээлт үүсгэж чадсангүй.", 503)
        try:
            enqueue_submission(
                submission_id=submission["id"],
                user_id=current_user["id"],
                problem_id=data["problem_id"],
                code=data["code"],
                language=language,
            )
        except Exception:
            db.update_submission_status(submission["id"], "error")
            return error_response("evaluator_unavailable", "The submission evaluator is temporarily unavailable.", "Илгээлтийн үнэлгээний систем түр боломжгүй байна.", 503)
        return {
            "message": "Submission received. Evaluating...",
            "submission": {
                "id": submission["id"],
                "status": submission.get("status", "pending"),
                "language": language,
                "created_at": submission.get("created_at"),
            },
        }, 202
    except Exception:
        return error_response("submission_service_unavailable", "The submission service is temporarily unavailable.", "Илгээлтийн үйлчилгээ түр боломжгүй байна.", 503)


@submissions_bp.route("/run", methods=["POST"])
@token_required
def run_code(current_user):
    """Execute code against visible tests without creating a graded submission."""
    if current_user.get("role") != "student":
        return error_response("student_only", "Only students can run code.", "Зөвхөн суралцагч код ажиллуулах боломжтой.", 403)
    data = request.get_json(silent=True) or {}
    if not data.get("problem_id") or not isinstance(data.get("code"), str) or not data["code"].strip():
        return error_response("validation_error", "Problem ID and non-empty code are required.", "Бодлогын ID болон хоосон биш код шаардлагатай.", 400)
    try:
        problem = db.get_problem(data["problem_id"])
        if not problem:
            return error_response("problem_not_found", "Problem not found.", "Бодлого олдсонгүй.", 404)
        language = str(data.get("language") or problem.get("language") or "python").lower()
        if language not in {"python", "javascript"}:
            return error_response("unsupported_language", "Unsupported programming language.", "Дэмжигдээгүй програмчлалын хэл.", 400)
        test_cases = db.get_test_cases(data["problem_id"], include_hidden=False)
        if not test_cases:
            return error_response("visible_tests_unavailable", "No visible test cases are available.", "Харагдах тестийн тохиолдол алга.", 409)
        result = get_executor().execute_test_cases(code=data["code"], language=language, test_cases=test_cases)
        return {"mode": "runtime", "problem_id": data["problem_id"], **result}, 200
    except Exception:
        return error_response("runtime_unavailable", "Runtime execution is temporarily unavailable.", "Код ажиллуулах систем түр боломжгүй байна.", 503)


@submissions_bp.route("/<int:submission_id>", methods=["GET"])
@token_required
def get_submission(current_user, submission_id):
    try:
        submission = db.get_submission(submission_id)
        if not submission:
            return error_response("submission_not_found", "Submission not found.", "Илгээлт олдсонгүй.", 404)
        if not _submission_access_allowed(submission, current_user):
            return error_response("permission_denied", "You do not have permission to view this submission.", "Танд энэ илгээлтийг харах зөвшөөрөл байхгүй.", 403)
        results = db.client.table("submission_results").select("*").eq("submission_id", submission_id).execute()
        return {"submission": submission, "results": _result_payload(results.data, current_user)}, 200
    except Exception:
        return error_response("submission_result_unavailable", "Submission results are temporarily unavailable.", "Илгээлтийн үр дүн түр боломжгүй байна.", 503)


@submissions_bp.route("/<int:submission_id>/stream", methods=["GET"])
@token_required
def stream_submission(current_user, submission_id):
    """Stream state changes until a terminal evaluator state is reached."""
    try:
        submission = db.get_submission(submission_id)
    except Exception:
        return error_response("submission_unavailable", "Submission status is temporarily unavailable.", "Илгээлтийн төлөв түр боломжгүй байна.", 503)
    if not submission:
        return error_response("submission_not_found", "Submission not found.", "Илгээлт олдсонгүй.", 404)
    if not _submission_access_allowed(submission, current_user):
        return error_response("permission_denied", "You do not have permission to view this submission.", "Танд энэ илгээлтийг харах зөвшөөрөл байхгүй.", 403)

    @stream_with_context
    def events():
        last_signature = None
        deadline = time.monotonic() + 90
        while time.monotonic() < deadline:
            current = db.get_submission(submission_id)
            results = db.client.table("submission_results").select("*").eq("submission_id", submission_id).execute()
            payload = {"submission": current, "results": _result_payload(results.data, current_user)}
            signature = json.dumps(payload, sort_keys=True, default=str)
            if signature != last_signature:
                yield f"event: submission\ndata: {json.dumps(payload, default=str)}\n\n"
                last_signature = signature
            if current and current.get("status") in _FINAL_STATES:
                break
            time.sleep(1)

    return Response(
        events(),
        mimetype="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no", "Connection": "keep-alive"},
    )


@submissions_bp.route("/user/<int:user_id>", methods=["GET"])
@token_required
def get_user_submissions(current_user, user_id):
    if current_user.get("id") != user_id and not _staff_user(current_user):
        return error_response("permission_denied", "You do not have permission to view these submissions.", "Танд эдгээр илгээлтийг харах зөвшөөрөл байхгүй.", 403)
    try:
        limit = max(1, min(request.args.get("limit", 50, type=int), 100))
        offset = max(0, request.args.get("offset", 0, type=int))
        submissions = (
            db.client.table("submissions")
            .select("*")
            .eq("user_id", user_id)
            .range(offset, offset + limit - 1)
            .order("created_at", desc=True)
            .execute()
        )
        return {"submissions": submissions.data or [], "total": len(submissions.data or []), "limit": limit, "offset": offset}, 200
    except Exception:
        return error_response("submission_history_unavailable", "Submission history is temporarily unavailable.", "Илгээлтийн түүх түр боломжгүй байна.", 503)
