"""Learning analytics and progress tracking routes."""

from flask import Blueprint

from backend.api.auth import token_required
from backend.db import db
from backend.rbac import any_permission_required, error_response


analytics_bp = Blueprint("analytics", __name__)


@analytics_bp.route("/dashboard", methods=["GET"])
@token_required
@any_permission_required(("student.dashboard.read", "teacher.dashboard.read", "platform.read"))
def get_dashboard(current_user):
    """Return real dashboard data for the authenticated role."""
    try:
        mastery_data = db.get_user_mastery(current_user["id"]) or []
        submissions = db.get_user_submissions(current_user["id"], limit=5) or []
        recent_practice = []
        for submission in submissions:
            problem = submission.get("problems") or {}
            score = submission.get("score")
            recent_practice.append(
                {
                    "id": submission.get("id"),
                    "problem_id": submission.get("problem_id"),
                    "title": problem.get("title") or f"Problem #{submission.get('problem_id')}",
                    "category": str(problem.get("difficulty", "Practice")).title(),
                    "status": str(submission.get("status", "pending")).replace("_", " ").title(),
                    "score": f"{float(score):.0f}%" if score is not None else "—",
                    "icon": str(submission.get("problem_id", 0)).zfill(2),
                    "created_at": submission.get("created_at"),
                }
            )
        return {
            "user_id": current_user["id"],
            "role": current_user.get("role", "student"),
            "mastery": mastery_data,
            "skills": mastery_data,
            "recentPractice": recent_practice,
            "recent_practice": recent_practice,
            "total_skills": len(mastery_data),
            "message": "Dashboard loaded.",
            "message_mn": "Хяналтын самбар ачааллаа.",
        }, 200
    except Exception:
        return {
            "error": {
                "code": "dashboard_failed",
                "message": "The dashboard could not be loaded.",
                "message_mn": "Хяналтын самбар ачаалахад алдаа гарлаа.",
            }
        }, 503


@analytics_bp.route("/mastery/<int:user_id>", methods=["GET"])
@token_required
def get_user_mastery(current_user, user_id):
    """Get mastery data only for the user or an authorized staff role."""
    if current_user["id"] != user_id and current_user["role"] not in {"owner", "admin", "teacher"}:
        return error_response(
            "permission_denied",
            "You do not have permission to view this data.",
            "Танд энэ мэдээллийг харах зөвшөөрөл байхгүй байна.",
            403,
        )
    try:
        mastery_data = db.get_user_mastery(user_id) or []
        return {"user_id": user_id, "mastery": mastery_data, "total_skills": len(mastery_data)}, 200
    except Exception:
        return error_response(
            "mastery_unavailable",
            "Mastery data is temporarily unavailable.",
            "Чадварын мэдээлэл түр боломжгүй байна.",
            503,
        )


@analytics_bp.route("/skill/<int:skill_id>", methods=["GET"])
@token_required
@any_permission_required(("analytics.read", "analytics.read.assigned", "analytics.read.own"))
def get_skill_statistics(current_user, skill_id):
    """Get aggregate skill statistics for an authorized user."""
    try:
        mastery_data = db.client.table("mastery_snapshots").select("*").eq("skill_id", skill_id).execute()
        records = mastery_data.data or []
        scores = [m.get("mastery_score", 0) for m in records]
        return {
            "skill_id": skill_id,
            "statistics": {
                "total_students": len(records),
                "average_mastery": sum(scores) / len(scores) if scores else 0,
                "min_mastery": min(scores) if scores else 0,
                "max_mastery": max(scores) if scores else 0,
            },
        }, 200
    except Exception:
        return error_response(
            "skill_statistics_unavailable",
            "Skill statistics are temporarily unavailable.",
            "Чадварын статистик түр боломжгүй байна.",
            503,
        )


@analytics_bp.route("/problem/<int:problem_id>", methods=["GET"])
@token_required
@any_permission_required(("analytics.read", "analytics.read.assigned"))
def get_problem_statistics(current_user, problem_id):
    """Get problem statistics for authorized staff."""
    try:
        problem = db.get_problem(problem_id)
        if not problem:
            return error_response("problem_not_found", "Problem not found.", "Бодлого олдсонгүй.", 404)
        submissions = db.client.table("submissions").select("*").eq("problem_id", problem_id).execute()
        records = submissions.data or []
        total = len(records)
        accepted = len([item for item in records if item.get("status") == "accepted"])
        scores = [item.get("score", 0) or 0 for item in records]
        return {
            "problem_id": problem_id,
            "statistics": {
                "total_submissions": total,
                "accepted_submissions": accepted,
                "acceptance_rate": accepted / total * 100 if total else 0,
                "average_score": sum(scores) / len(scores) if scores else 0,
                "difficulty": problem.get("difficulty"),
            },
        }, 200
    except Exception:
        return error_response(
            "problem_statistics_unavailable",
            "Problem statistics are temporarily unavailable.",
            "Бодлогын статистик түр боломжгүй байна.",
            503,
        )
