"""Authenticated profile, progress, and quiz persistence endpoints."""

from typing import Literal

from flask import Blueprint, request
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from backend.api.auth import token_required
from backend.db import db
from backend.services.gamification import get_summary
from backend.rbac import error_response
from course_data import COURSE_CATALOG

learning_bp = Blueprint("learning", __name__)


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProfileUpdate(StrictModel):
    display_name: str | None = Field(default=None, min_length=1, max_length=80)
    locale: Literal["mn", "en"] | None = None
    theme: Literal["light", "dark", "system"] | None = None


class CourseProgressUpdate(StrictModel):
    course_slug: Literal["python", "html", "css", "javascript"]
    progress_percent: int = Field(ge=0, le=100)


class LessonProgressUpdate(StrictModel):
    course_slug: Literal["python", "html", "css", "javascript"]
    lesson_slug: str = Field(min_length=1, max_length=96, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    completed: bool = True


class QuizAttemptCreate(StrictModel):
    course_slug: Literal["python", "html", "css", "javascript"]
    lesson_slug: str = Field(min_length=1, max_length=96, pattern=r"^[a-z0-9][a-z0-9_-]*$")
    score: int = Field(default=0, ge=0)
    total_questions: int = Field(default=1, gt=0, le=100)
    answers: list[dict] = Field(default_factory=list, max_length=100)
    answer: str | None = Field(default=None, max_length=500)


def _validated(model):
    try:
        return model.model_validate(request.get_json(silent=True) or {}), None
    except ValidationError as error:
        return None, error_response(
            "invalid_request", "The request body is invalid.", "Хүсэлтийн өгөгдөл буруу байна.", 400,
            details=error.errors(include_url=False, include_input=False),
        )


def _identity(current_user):
    identity = current_user.get("auth_user_id")
    if not identity:
        return None, error_response(
            "supabase_identity_required",
            "Sign in again with Supabase Auth before saving learning data.",
            "Ахиц хадгалахын тулд Supabase Auth-аар дахин нэвтэрнэ үү.",
            409,
        )
    return str(identity), None


@learning_bp.route("/profile", methods=["GET", "PATCH"])
@token_required
def profile(current_user):
    user_id, error = _identity(current_user)
    if error:
        return error
    if request.method == "GET":
        return {"profile": db.get_profile(user_id)}, 200
    body, error = _validated(ProfileUpdate)
    if error:
        return error
    changes = body.model_dump(exclude_none=True)
    if not changes:
        return error_response("empty_update", "No profile changes were supplied.", "Өөрчлөх мэдээлэл ирсэнгүй.", 400)
    return {"profile": db.update_profile(user_id, changes)}, 200


def _catalog_summary(progress):
    """Adapt canonical UUID progress rows to the learner-facing catalog contract."""
    lesson_rows = progress.get("lesson_progress", []) if isinstance(progress, dict) else []
    completed = {
        (str(row.get("course_slug")), str(row.get("lesson_slug")))
        for row in lesson_rows
        if row.get("course_slug") and row.get("lesson_slug")
    }
    courses = []
    for course_slug, course in COURSE_CATALOG.items():
        lessons = [lesson for module in course.get("modules", []) for lesson in module.get("lessons", [])]
        course_completed = sum((course_slug, str(lesson.get("id"))) in completed for lesson in lessons)
        total = len(lessons)
        next_lesson = next(
            (lesson for lesson in lessons if (course_slug, str(lesson.get("id"))) not in completed),
            None,
        )
        courses.append({
            "course_id": course_slug,
            "title": course.get("title", course_slug),
            "total_lessons": total,
            "completed_lessons": course_completed,
            "progress_percent": round((course_completed / total) * 100) if total else 0,
            "next_lesson_slug": next_lesson.get("id") if next_lesson else None,
            "next_lesson_title": next_lesson.get("title") if next_lesson else None,
        })
    total_lessons = sum(item["total_lessons"] for item in courses)
    completed_lessons = sum(item["completed_lessons"] for item in courses)
    recommended = next((course for course in courses if course.get("next_lesson_slug")), None)
    return {
        "courses": courses,
        "completed_lessons": completed_lessons,
        "total_lessons": total_lessons,
        "overall_percent": round((completed_lessons / total_lessons) * 100) if total_lessons else 0,
        "completed_lesson_keys": [f"{course}:{lesson}" for course, lesson in sorted(completed)],
        "next_recommended": {
            "course_id": recommended["course_id"],
            "lesson_slug": recommended["next_lesson_slug"],
            "lesson_title": recommended["next_lesson_title"],
        } if recommended else None,
    }


@learning_bp.route("/summary", methods=["GET"])
@token_required
def summary(current_user):
    user_id, error = _identity(current_user)
    if error:
        return error
    try:
        return _catalog_summary(db.get_learning_progress(user_id)), 200
    except Exception:
        return error_response(
            "progress_unavailable",
            "Learning progress is temporarily unavailable.",
            "Сургалтын ахиц түр боломжгүй байна.",
            503,
        )


@learning_bp.route("/progress", methods=["GET", "PUT"])
@token_required
def progress(current_user):
    user_id, error = _identity(current_user)
    if error:
        return error
    if request.method == "GET":
        return db.get_learning_progress(user_id), 200
    body, error = _validated(CourseProgressUpdate)
    if error:
        return error
    return {"course_progress": db.upsert_course_progress(user_id, body.model_dump())}, 200


@learning_bp.route("/lessons", methods=["PUT"])
@token_required
def lesson_progress(current_user):
    user_id, error = _identity(current_user)
    if error:
        return error
    body, error = _validated(LessonProgressUpdate)
    if error:
        return error
    values = body.model_dump()
    completed = values.pop("completed")
    result = db.set_lesson_progress(user_id, values, completed)
    return {"lesson_progress": result, "completed": completed}, 200


@learning_bp.route("/gamification", methods=["GET"])
@token_required
def gamification(current_user):
    try:
        return get_summary(int(current_user["id"])), 200
    except Exception:
        return error_response(
            "gamification_unavailable",
            "Gamification summary is temporarily unavailable.",
            "XP болон badge-ийн мэдээлэл түр боломжгүй байна.",
            503,
        )


def _normalize_quiz_text(value: str) -> str:
    return "".join(character.lower() for character in value if character.isalnum())


def _quiz_answer_result(course_slug: str, lesson_slug: str, answer: str):
    course = COURSE_CATALOG.get(course_slug)
    lesson = next(
        (
            item
            for module in (course or {}).get("modules", [])
            for item in module.get("lessons", [])
            if item.get("id") == lesson_slug
        ),
        None,
    )
    expected = str(((lesson or {}).get("quiz") or {}).get("answer") or "")
    actual_normalized = _normalize_quiz_text(answer)
    expected_normalized = _normalize_quiz_text(expected)
    if not lesson or not expected_normalized or len(actual_normalized) < 3:
        return False, expected
    correct = (
        actual_normalized == expected_normalized
        or actual_normalized in expected_normalized and len(actual_normalized) >= 4
        or expected_normalized in actual_normalized
    )
    return correct, expected


@learning_bp.route("/quiz-attempts", methods=["GET", "POST"])
@token_required
def quiz_attempts(current_user):
    user_id, error = _identity(current_user)
    if error:
        return error
    if request.method == "GET":
        return {"quiz_attempts": db.get_quiz_attempts(user_id)}, 200
    body, error = _validated(QuizAttemptCreate)
    if error:
        return error
    values = body.model_dump()
    answer = values.get("answer")
    if answer is not None:
        correct, _ = _quiz_answer_result(values["course_slug"], values["lesson_slug"], answer)
        values["score"] = 1 if correct else 0
        values["total_questions"] = 1
        values["answers"] = [{"answer": answer, "correct": correct}]
    if values["score"] > values["total_questions"]:
        return error_response("invalid_score", "Score exceeds total questions.", "Оноо асуултын тооноос их байна.", 400)
    attempt = db.create_quiz_attempt(user_id, values)
    if answer is not None:
        attempt = {**(attempt or {}), "correct": values["score"] == 1, "score": values["score"], "total_questions": 1}
    return {"quiz_attempt": attempt}, 201
