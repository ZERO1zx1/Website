"""Content Studio API for admins and owners."""

import hashlib

from flask import Blueprint, request

from backend.api.auth import admin_required
from backend.db import db

admin_content_bp = Blueprint("admin_content", __name__)

_CONTENT_TYPES = {"lesson", "exercise", "bug_lab", "guided_project", "portfolio_project"}
_DIFFICULTIES = {"easy", "medium", "hard", "beginner", "intermediate", "advanced"}
_STATUSES = {"draft", "review", "published", "archived"}


def _difficulty(value):
    return {"beginner": "easy", "intermediate": "medium", "advanced": "hard"}.get(value, value)


def _problem_payload(data, current_user):
    title = str(data.get("title", "")).strip()
    description = str(data.get("description", "")).strip()
    starter_code = str(data.get("starter_code", ""))
    content_type = str(data.get("content_type", "exercise")).strip().lower()
    difficulty = str(data.get("difficulty", "easy")).strip().lower()
    language = str(data.get("language", "python")).strip().lower()
    status = str(data.get("status", "draft")).strip().lower()
    if not title or not description or not starter_code:
        raise ValueError("title, description and starter_code are required")
    if content_type not in _CONTENT_TYPES:
        raise ValueError("Invalid content_type")
    if difficulty not in _DIFFICULTIES:
        raise ValueError("Invalid difficulty")
    if language not in {"python", "javascript", "html", "css"}:
        raise ValueError("Unsupported language")
    if status not in _STATUSES:
        raise ValueError("Invalid status")
    xp_reward = int(data.get("xp_reward", data.get("xp", 80)))
    if xp_reward < 0 or xp_reward > 5000:
        raise ValueError("xp_reward must be between 0 and 5000")
    slug = str(data.get("slug", "")).strip().lower() or None
    return {
        "title": title,
        "description": description,
        "difficulty": _difficulty(difficulty),
        "starter_code": starter_code,
        "created_by": current_user["id"],
        "language": language,
        "slug": slug,
        "content_type": content_type,
        "course_slug": str(data.get("course_slug", "")).strip() or None,
        "lesson_slug": str(data.get("lesson_slug", "")).strip() or None,
        "xp_reward": xp_reward,
        "status": status,
        "explanation": str(data.get("explanation", "")),
    }


@admin_content_bp.route("", methods=["GET"])
@admin_required
def list_content(current_user):
    limit = max(1, min(request.args.get("limit", 100, type=int), 200))
    offset = max(0, request.args.get("offset", 0, type=int))
    try:
        rows = db.get_problems(limit=limit, offset=offset)
        return {"content": rows or [], "limit": limit, "offset": offset, "total": len(rows or [])}, 200
    except Exception:
        return {"error": "Content catalog unavailable"}, 503


@admin_content_bp.route("", methods=["POST"])
@admin_required
def create_content(current_user):
    data = request.get_json(silent=True) or {}
    try:
        payload = _problem_payload(data, current_user)
        problem = db.create_problem(
            title=payload["title"], description=payload["description"],
            difficulty=payload["difficulty"], starter_code=payload["starter_code"],
            created_by=current_user["id"], language=payload["language"],
        )
        if not problem:
            return {"error": "Content could not be created"}, 500
        problem_id = problem["id"]
        metadata = {key: payload[key] for key in ("slug", "content_type", "course_slug", "lesson_slug", "xp_reward", "status", "explanation")}
        db.client.table("problems").update(metadata).eq("id", problem_id).execute()
        db.client.table("problem_versions").insert({
            "problem_id": problem_id,
            "version_number": 1,
            "content_hash": hashlib.sha256((payload["starter_code"] + payload["description"]).encode()).hexdigest(),
        }).execute()
        tests = []
        for item in data.get("tests", []):
            if not isinstance(item, dict) or "expected_output" not in item:
                return {"error": "Each test needs expected_output"}, 400
            tests.append(db.create_test_case(
                problem_id=problem_id,
                input_data=str(item.get("input", "")),
                expected_output=str(item["expected_output"]),
                is_hidden=bool(item.get("is_hidden", item.get("visibility") == "hidden")),
            ))
        hints = []
        for index, content in enumerate(data.get("hints", []), start=1):
            if not str(content).strip():
                continue
            result = db.client.table("hints").insert({"problem_id": problem_id, "level": index, "content": str(content)}).execute()
            hints.append(result.data[0] if result.data else None)
        return {"message": "Content created", "content": {**problem, **metadata}, "tests": tests, "hints": hints}, 201
    except (TypeError, ValueError) as error:
        return {"error": str(error)}, 400
    except Exception:
        return {"error": "Content creation failed"}, 503
