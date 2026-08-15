"""Training assessment APIs for exam builders and student attempts."""

from flask import Blueprint, request

from backend.api.auth import token_required
from backend.db import db
from backend.rbac import any_permission_required, error_response, permission_required


exams_bp = Blueprint("exams", __name__)


def _error(code, message, message_mn, status):
    return error_response(code, message, message_mn, status)


def _validate_exam(data):
    title = str(data.get("title", "")).strip()
    if len(title) < 3:
        return "title_invalid", "Exam title must be at least 3 characters.", "Шалгалтын нэр хамгийн багадаа 3 тэмдэгттэй байна."
    try:
        duration = int(data.get("duration_minutes", 20))
        attempts = int(data.get("max_attempts", 3))
    except (TypeError, ValueError):
        return "exam_settings_invalid", "Duration and attempt limit must be numbers.", "Хугацаа болон оролдлогын хязгаар тоо байна."
    if not 5 <= duration <= 180:
        return "duration_invalid", "Duration must be between 5 and 180 minutes.", "Шалгалтын хугацаа 5–180 минутын хооронд байна."
    if not 1 <= attempts <= 10:
        return "attempt_limit_invalid", "Attempt limit must be between 1 and 10.", "Оролдлогын хязгаар 1–10 байна."
    questions = data.get("questions")
    if not isinstance(questions, list) or not 1 <= len(questions) <= 50:
        return "questions_invalid", "Add between 1 and 50 questions.", "1–50 асуулт нэмнэ үү."
    for question in questions:
        if len(str(question.get("prompt", "")).strip()) < 5:
            return "question_invalid", "Every question needs a prompt.", "Асуулт бүр prompt-той байна."
        question_type = question.get("question_type", "multiple_choice")
        if question_type not in {"multiple_choice", "short_answer"}:
            return "question_type_invalid", "This builder currently supports multiple-choice and short-answer questions.", "Одоогийн builder multiple-choice болон short-answer асуултыг дэмжинэ."
        if question_type == "multiple_choice" and not isinstance(question.get("options"), list):
            return "options_invalid", "Multiple-choice questions need options.", "Сонгох асуулт options-той байна."
        if not str(question.get("correct_answer", "")).strip():
            return "answer_invalid", "Every question needs a correct answer.", "Асуулт бүр зөв хариулттай байна."
    return None


@exams_bp.route("", methods=["GET"])
@token_required
@any_permission_required(("exams.read", "student.dashboard.read", "teacher.dashboard.read", "platform.read"))
def list_exams(current_user):
    try:
        return {"exams": db.get_exams_for_user(current_user["id"], current_user.get("role", "student"))}, 200
    except Exception:
        return _error("exams_unavailable", "Exams are temporarily unavailable.", "Шалгалтын мэдээлэл түр боломжгүй байна.", 503)


@exams_bp.route("", methods=["POST"])
@token_required
@permission_required("exams.manage")
def create_exam(current_user):
    data = request.get_json(silent=True) or {}
    validation = _validate_exam(data)
    if validation:
        return _error(*validation, 400)
    try:
        exam = db.create_exam(data, current_user["id"])
        return {"message": "Exam created.", "exam": exam}, 201
    except Exception:
        return _error("exam_create_failed", "The exam could not be created.", "Шалгалт үүсгэж чадсангүй.", 503)


@exams_bp.route("/<int:exam_id>", methods=["GET"])
@token_required
@any_permission_required(("exams.read", "student.dashboard.read", "teacher.dashboard.read", "platform.read"))
def get_exam(current_user, exam_id):
    include_answers = current_user.get("role") in {"owner", "admin", "teacher"}
    try:
        exam = db.get_exam(exam_id, include_answers=include_answers)
        if not exam or (current_user.get("role") == "student" and exam.get("status") != "published"):
            return _error("exam_not_found", "Exam not found.", "Шалгалт олдсонгүй.", 404)
        return {"exam": exam}, 200
    except Exception:
        return _error("exam_unavailable", "The exam could not be loaded.", "Шалгалтыг ачаалж чадсангүй.", 503)


@exams_bp.route("/<int:exam_id>/attempts", methods=["POST"])
@token_required
@permission_required("exams.attempt")
def start_exam(current_user, exam_id):
    if current_user.get("role") != "student":
        return _error("student_only", "Only students can start an exam.", "Зөвхөн суралцагч шалгалт эхлүүлнэ.", 403)
    try:
        attempt, problem = db.start_exam(exam_id, current_user["id"])
        if problem == "attempt_limit_reached":
            return _error(problem, "You have used all attempts for this exam.", "Та энэ шалгалтын бүх оролдлогоо ашигласан байна.", 409)
        if problem or not attempt:
            return _error(problem or "exam_not_available", "This exam is not available.", "Энэ шалгалт одоогоор боломжгүй байна.", 404)
        return {"attempt": attempt}, 201
    except Exception:
        return _error("attempt_start_failed", "The exam attempt could not be started.", "Шалгалтын оролдлого эхлүүлж чадсангүй.", 503)


@exams_bp.route("/attempts/<int:attempt_id>", methods=["GET"])
@token_required
@any_permission_required(("exams.attempts.read.own", "exams.attempts.read.assigned", "exams.attempts.read", "platform.read"))
def get_attempt(current_user, attempt_id):
    own_id = current_user["id"] if current_user.get("role") == "student" else None
    try:
        attempt = db.get_attempt(attempt_id, user_id=own_id, include_answers=False)
        if not attempt:
            return _error("attempt_not_found", "Exam attempt not found.", "Шалгалтын оролдлого олдсонгүй.", 404)
        if current_user.get("role") == "teacher" and attempt.get("exam", {}).get("created_by") != current_user.get("id"):
            return _error("permission_denied", "You can only view attempts for your own exams.", "Та зөвхөн өөрийн шалгалтын оролдлогыг харна.", 403)
        return {"attempt": attempt}, 200
    except Exception:
        return _error("attempt_unavailable", "The exam attempt could not be loaded.", "Шалгалтын оролдлогыг ачаалж чадсангүй.", 503)


@exams_bp.route("/attempts/<int:attempt_id>/answers/<int:question_id>", methods=["PATCH"])
@token_required
@permission_required("exams.attempt")
def save_answer(current_user, attempt_id, question_id):
    if current_user.get("role") != "student":
        return _error("student_only", "Only students can answer an exam.", "Зөвхөн суралцагч шалгалтад хариулна.", 403)
    payload = request.get_json(silent=True) or {}
    answer = str(payload.get("answer", ""))[:5000]
    try:
        attempt = db.get_attempt(attempt_id, user_id=current_user["id"], include_answers=False)
        if not attempt or attempt.get("status") != "in_progress":
            return _error("attempt_closed", "This exam attempt is no longer editable.", "Энэ оролдлогыг дахин засах боломжгүй.", 409)
        if question_id not in {question.get("id") for question in attempt.get("exam", {}).get("questions", [])}:
            return _error("question_not_found", "Question does not belong to this exam.", "Асуулт энэ шалгалтад хамаарахгүй байна.", 404)
        saved = db.save_exam_answer(attempt_id, question_id, answer)
        return {"answer": saved, "saved": True}, 200
    except Exception:
        return _error("answer_save_failed", "The answer could not be saved.", "Хариултыг хадгалж чадсангүй.", 503)


@exams_bp.route("/attempts/<int:attempt_id>/submit", methods=["POST"])
@token_required
@permission_required("exams.attempt")
def submit_exam(current_user, attempt_id):
    if current_user.get("role") != "student":
        return _error("student_only", "Only students can submit an exam.", "Зөвхөн суралцагч шалгалт илгээнэ.", 403)
    try:
        attempt, problem = db.submit_exam(attempt_id, current_user["id"])
        if problem or not attempt:
            return _error(problem or "attempt_not_found", "The exam attempt could not be submitted.", "Шалгалтын оролдлогыг илгээж чадсангүй.", 404)
        return {"message": "Exam submitted.", "attempt": attempt}, 200
    except Exception:
        return _error("exam_submit_failed", "The exam could not be submitted.", "Шалгалтыг илгээж чадсангүй.", 503)


@exams_bp.route("/<int:exam_id>/report", methods=["GET"])
@token_required
@permission_required("analytics.exams.read")
def exam_report(current_user, exam_id):
    if current_user.get("role") == "student":
        return _error("permission_denied", "Students cannot view aggregate exam reports.", "Суралцагч aggregate шалгалтын тайлан харахгүй.", 403)
    try:
        exam = db.get_exam(exam_id, include_answers=False)
        if not exam:
            return _error("exam_not_found", "Exam not found.", "Шалгалт олдсонгүй.", 404)
        if current_user.get("role") == "teacher" and exam.get("created_by") != current_user.get("id"):
            return _error("permission_denied", "You can only view reports for your own exams.", "Та зөвхөн өөрийн шалгалтын тайланг харна.", 403)
        report = db.get_exam_report(exam_id)
        return {"report": report}, 200
    except Exception:
        return _error("exam_report_failed", "The exam report could not be loaded.", "Шалгалтын тайланг ачаалж чадсангүй.", 503)
