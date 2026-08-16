"""Analytics calculations derived from persisted learning activity."""

from __future__ import annotations

from datetime import date, datetime, timedelta, timezone


def _parse_timestamp(value) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
    except (TypeError, ValueError):
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed


def summarize_learning_activity(
    lesson_progress: list[dict],
    lessons: list[dict],
    *,
    today: date | None = None,
) -> dict:
    """Return persisted lesson activity metrics without inventing daily data.

    The local/Supabase schema currently records lesson lifecycle timestamps and
    lesson estimated duration, rather than foreground browser time. Therefore
    the API labels the total as estimated study minutes and derives activity
    only from rows that actually exist in ``lesson_progress``.
    """
    today = today or datetime.now(timezone.utc).date()
    duration_by_lesson = {
        int(lesson["id"]): max(1, int(lesson.get("estimated_minutes") or 20))
        for lesson in lessons
        if lesson.get("id") is not None
    }
    daily_minutes = {
        today - timedelta(days=offset): 0
        for offset in range(6, -1, -1)
    }
    active_dates: set[date] = set()
    study_minutes = 0

    for progress in lesson_progress or []:
        lesson_id = progress.get("lesson_id")
        minutes = duration_by_lesson.get(int(lesson_id), 20) if lesson_id is not None else 20
        timestamp = _parse_timestamp(progress.get("completed_at") or progress.get("started_at"))
        if timestamp is None:
            continue
        activity_date = timestamp.astimezone(timezone.utc).date()
        active_dates.add(activity_date)
        study_minutes += minutes
        if activity_date in daily_minutes:
            daily_minutes[activity_date] += minutes

    streak = 0
    cursor = today
    while cursor in active_dates:
        streak += 1
        cursor -= timedelta(days=1)

    return {
        "study_minutes": study_minutes,
        "current_streak": streak,
        "daily_activity": [
            {"date": activity_date.isoformat(), "minutes": minutes}
            for activity_date, minutes in daily_minutes.items()
        ],
    }
