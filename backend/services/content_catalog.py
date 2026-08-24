"""Learner-facing content catalog with published DB precedence and static fallback."""

from __future__ import annotations

from collections.abc import Iterable


_CONTENT_TYPES = {"lesson", "exercise", "bug_lab", "guided_project", "portfolio_project"}


def _normalize_problem(row: dict) -> dict | None:
    """Map a published problem row into the shape used by practice/workspace pages."""
    if not isinstance(row, dict) or row.get("status") != "published":
        return None
    slug = str(row.get("slug") or f"problem-{row.get('id')}").strip()
    course_id = str(row.get("course_slug") or "").strip()
    if not slug or not course_id:
        return None
    content_type = str(row.get("content_type") or "exercise").strip()
    if content_type not in _CONTENT_TYPES:
        return None
    difficulty = str(row.get("difficulty") or "beginner").strip().lower()
    difficulty = {"easy": "beginner", "medium": "intermediate", "hard": "advanced"}.get(difficulty, difficulty)
    title = str(row.get("title") or slug).strip()
    description = str(row.get("description") or row.get("explanation") or "").strip()
    return {
        "id": slug,
        "problem_id": row.get("id"),
        "course_id": course_id,
        "type": content_type,
        "difficulty": difficulty,
        "title": title,
        "hook": (str(row.get("explanation") or description).split(".")[0] or title).strip(),
        "description": description,
        "starter_code": str(row.get("starter_code") or ""),
        "expected_output": "",
        "hint": "Hint-ээ challenge дотор нээгээрэй.",
        "xp": int(row.get("xp_reward") or 0),
        "lesson_id": str(row.get("lesson_slug") or ""),
        "language": str(row.get("language") or "python"),
    }


def merge_published_challenges(static_challenges: Iterable[dict], published_rows: Iterable[dict]) -> list[dict]:
    """DB rows override static items with the same slug; static items remain fallback."""
    normalized = [_normalize_problem(row) for row in published_rows]
    published = {item["id"]: item for item in normalized if item}
    result = []
    seen = set()
    for item in static_challenges:
        key = str(item.get("id", ""))
        if key in published:
            result.append(published[key])
        else:
            result.append(item)
        seen.add(key)
    result.extend(item for key, item in published.items() if key not in seen)
    return result


def load_challenges(db_gateway, static_challenges: Iterable[dict]) -> list[dict]:
    """Load published rows safely; an unavailable DB never removes the built-in catalog."""
    try:
        published_rows = db_gateway.get_published_content()
    except Exception:
        published_rows = []
    return merge_published_challenges(static_challenges, published_rows)
