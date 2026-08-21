"""Supabase-backed learner progress and preference endpoints."""

from collections import defaultdict

from flask import Blueprint, request

from backend.api.auth import token_required
from backend.db import db
from backend.rbac import error_response
from course_data import COURSE_CATALOG


progress_bp = Blueprint("progress", __name__)


def _course_lessons(course_id: str):
    course = COURSE_CATALOG.get(course_id)
    if not course:
        return None, []
    lessons = [lesson for module in course.get("modules", []) for lesson in module.get("lessons", [])]
    return course, lessons


def _summary_for(user_id: str, access_token: str):
    """Combine learner-owned RLS-scoped completions with the versioned course catalog."""
    completion_rows = db.get_lesson_progress(user_id, access_token)
    completed_by_course = defaultdict(set)
    for row in completion_rows:
        completed_by_course[row.get("course_id")].add(row.get("lesson_id"))

    courses = []
    for course_id, course in COURSE_CATALOG.items():
        _, lessons = _course_lessons(course_id)
        lesson_ids = {lesson.get("id") for lesson in lessons}
        completed_ids = completed_by_course[course_id] & lesson_ids
        total = len(lesson_ids)
        percent = round((len(completed_ids) / total) * 100) if total else 0
        courses.append({
            "course_id": course_id,
            "title": course.get("title", course_id),
            "total_lessons": total,
            "completed_lessons": len(completed_ids),
            "progress_percent": percent,
        })

    total_lessons = sum(course["total_lessons"] for course in courses)
    completed_lessons = sum(course["completed_lessons"] for course in courses)
    return {
        "courses": courses,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
        "overall_percent": round((completed_lessons / total_lessons) * 100) if total_lessons else 0,
        "completed_lesson_keys": [
            f"{row.get('course_id')}:{row.get('lesson_id')}" for row in completion_rows
            if row.get("course_id") in COURSE_CATALOG
        ],
    }


@progress_bp.route("", methods=["GET"])
@token_required
def get_progress(current_user):
    return _summary_for(current_user["id"], current_user["_access_token"]), 200


@progress_bp.route("/lessons", methods=["POST"])
@token_required
def complete_lesson(current_user):
    data = request.get_json(silent=True) or {}
    course_id = str(data.get("course_id", "")).strip()
    lesson_id = str(data.get("lesson_id", "")).strip()
    course, lessons = _course_lessons(course_id)
    if not course or lesson_id not in {lesson.get("id") for lesson in lessons}:
        return error_response(
            "unknown_lesson",
            "The requested lesson does not exist in the CodeCraft catalog.",
            "Сонгосон хичээл CodeCraft хөтөлбөрөөс олдсонгүй.",
            404,
        )
    try:
        token = current_user["_access_token"]
        db.complete_lesson(current_user["id"], token, course_id, lesson_id)
        summary = _summary_for(current_user["id"], token)
        course_summary = next(item for item in summary["courses"] if item["course_id"] == course_id)
        db.save_course_progress(current_user["id"], token, course_id, course_summary["progress_percent"])
        return {
            "message": "Lesson marked complete.",
            "message_mn": "Хичээлийг дууссанд тооцлоо.",
            "course": course_summary,
            "summary": summary,
        }, 200
    except Exception:
        return error_response(
            "progress_save_failed",
            "Learning progress could not be saved.",
            "Сургалтын явцыг хадгалах боломжгүй байна.",
            502,
        )


@progress_bp.route("/lessons/<course_id>/<lesson_id>", methods=["DELETE"])
@token_required
def remove_lesson_completion(current_user, course_id, lesson_id):
    course, lessons = _course_lessons(course_id)
    if not course or lesson_id not in {lesson.get("id") for lesson in lessons}:
        return error_response("unknown_lesson", "Lesson not found.", "Хичээл олдсонгүй.", 404)
    try:
        token = current_user["_access_token"]
        db.remove_lesson_completion(current_user["id"], token, course_id, lesson_id)
        summary = _summary_for(current_user["id"], token)
        course_summary = next(item for item in summary["courses"] if item["course_id"] == course_id)
        db.save_course_progress(current_user["id"], token, course_id, course_summary["progress_percent"])
        return {"message": "Lesson completion removed.", "message_mn": "Хичээлийн тэмдэглэгээг цуцаллаа.", "course": course_summary, "summary": summary}, 200
    except Exception:
        return error_response("progress_remove_failed", "Progress could not be updated.", "Сургалтын явцыг шинэчлэх боломжгүй байна.", 502)


@progress_bp.route("/profile", methods=["GET"])
@token_required
def get_profile(current_user):
    return {"profile": current_user}, 200


@progress_bp.route("/profile/preferences", methods=["PATCH"])
@token_required
def update_preferences(current_user):
    data = request.get_json(silent=True) or {}
    if "theme" in data and data["theme"] not in {"light", "dark", "system"}:
        return error_response("invalid_theme", "Theme must be light, dark, or system.", "Өнгөний горим light, dark эсвэл system байна.", 400)
    if "locale" in data and data["locale"] not in {"mn", "en"}:
        return error_response("invalid_locale", "Locale must be mn or en.", "Хэл mn эсвэл en байна.", 400)
    if "display_name" in data and (not isinstance(data["display_name"], str) or not data["display_name"].strip()):
        return error_response("invalid_name", "Display name is invalid.", "Хэрэглэгчийн нэр буруу байна.", 400)
    try:
        profile = db.update_profile_preferences(current_user["id"], current_user["_access_token"], data)
        public_profile = {
            "id": str(profile.get("id")),
            "email": profile.get("email"),
            "name": profile.get("display_name"),
            "role": profile.get("role", "student"),
            "locale": profile.get("locale", "mn"),
            "theme": profile.get("theme", "system"),
        }
        return {"message": "Preferences saved.", "message_mn": "Тохиргоог хадгаллаа.", "profile": public_profile}, 200
    except Exception:
        return error_response("preferences_save_failed", "Preferences could not be saved.", "Тохиргоог хадгалах боломжгүй байна.", 502)
