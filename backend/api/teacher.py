"""Teacher panel and class analytics API."""

from flask import Blueprint

from backend.api.auth import token_required
from backend.db import db
from backend.rbac import permission_required

teacher_bp = Blueprint("teacher", __name__)


@teacher_bp.route("/dashboard", methods=["GET"])
@token_required
@permission_required("teacher.dashboard.read")
def get_teacher_dashboard(current_user):
    """Return a role-aware teacher panel summary."""
    try:
        if current_user.get("role") in {"owner", "admin"}:
            classes = db.get_all_classes()
        else:
            classes = db.get_teacher_classes(current_user["id"])
        return {
            "role": current_user.get("role"),
            "classes": classes or [],
            "total_classes": len(classes or []),
            "total_students": sum(int(item.get("student_count", 0) or 0) for item in (classes or [])),
            "message": "Teacher dashboard loaded.",
            "message_mn": "Багшийн самбар ачааллаа.",
        }, 200
    except Exception:
        return {
            "error": {
                "code": "teacher_dashboard_failed",
                "message": "The teacher dashboard could not be loaded.",
                "message_mn": "Багшийн самбар ачаалахад алдаа гарлаа.",
            }
        }, 500


@teacher_bp.route("/classes/<int:class_id>/analytics", methods=["GET"])
@token_required
@permission_required("teacher.dashboard.read")
def get_class_analytics(current_user, class_id):
    """Return analytics only when the role/scope permits it."""
    try:
        class_obj = db.get_class(class_id)
        if not class_obj:
            return {
                "error": {
                    "code": "class_not_found",
                    "message": "Class not found.",
                    "message_mn": "Анги олдсонгүй.",
                }
            }, 404
        if current_user.get("role") == "teacher" and class_obj.get("teacher_id") != current_user.get("id"):
            return {
                "error": {
                    "code": "permission_denied",
                    "message": "You can only view analytics for your own classes.",
                    "message_mn": "Та зөвхөн өөрийн ангийн мэдээллийг харах боломжтой.",
                }
            }, 403
        return {
            "class_id": class_id,
            "analytics": {
                "total_students": class_obj.get("student_count", 0),
                "average_mastery": class_obj.get("average_mastery", 0),
                "assignment_completion_rate": class_obj.get("assignment_completion_rate", 0),
            },
        }, 200
    except Exception:
        return {
            "error": {
                "code": "class_analytics_failed",
                "message": "Class analytics could not be loaded.",
                "message_mn": "Ангийн аналитик ачаалахад алдаа гарлаа.",
            }
        }, 500
