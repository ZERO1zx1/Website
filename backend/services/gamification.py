"""Server-side rewards for verified learning activity.

The evaluator is the only caller that should award challenge XP. Every reward
uses a unique event_key, so retries from a worker cannot double-award points.
"""

import logging
from datetime import date, timedelta

from backend.db import db

logger = logging.getLogger(__name__)


def _level_for_xp(total_xp: int) -> int:
    return max(1, (int(total_xp) // 500) + 1)


def _profile(user_id: int):
    result = db.client.table("gamification_profiles").select("*").eq("user_id", user_id).limit(1).execute()
    return result.data[0] if result.data else None


def _ensure_profile(user_id: int):
    current = _profile(user_id)
    if current:
        return current
    result = db.client.table("gamification_profiles").insert({"user_id": user_id}).execute()
    return result.data[0] if result.data else {"user_id": user_id, "total_xp": 0, "level": 1, "current_streak": 0, "longest_streak": 0}


def record_activity(user_id: int, source_type: str, source_id: int | None = None, activity_day: date | None = None):
    """Record one meaningful learning day and update current/longest streak."""
    today = activity_day or date.today()
    db.client.table("learning_streaks").upsert({
        "user_id": user_id, "activity_date": today.isoformat(), "source_type": source_type, "source_id": source_id,
    }, on_conflict="user_id,activity_date").execute()
    profile = _ensure_profile(user_id)
    last_day = profile.get("last_activity_date")
    current = int(profile.get("current_streak") or 0)
    if str(last_day) == today.isoformat():
        return profile
    if last_day and str(last_day) == (today - timedelta(days=1)).isoformat():
        current += 1
    else:
        current = 1
    longest = max(int(profile.get("longest_streak") or 0), current)
    result = db.client.table("gamification_profiles").update({
        "current_streak": current, "longest_streak": longest, "last_activity_date": today.isoformat(),
    }).eq("user_id", user_id).execute()
    return result.data[0] if result.data else {**profile, "current_streak": current, "longest_streak": longest}


def award_xp(user_id: int, event_key: str, event_type: str, xp_amount: int, source_id: int | None = None, metadata: dict | None = None):
    """Award XP exactly once, then refresh the user's level."""
    if xp_amount <= 0:
        return {"awarded": False, "xp_amount": 0, "reason": "non_positive_reward"}
    existing = db.client.table("xp_events").select("id,xp_amount").eq("user_id", user_id).eq("event_key", event_key).limit(1).execute()
    if existing.data:
        return {"awarded": False, "xp_amount": 0, "reason": "already_awarded"}
    db.client.table("xp_events").insert({
        "user_id": user_id, "event_key": event_key, "event_type": event_type,
        "source_id": source_id, "xp_amount": xp_amount, "metadata": metadata or {},
    }).execute()
    profile = _ensure_profile(user_id)
    total = int(profile.get("total_xp") or 0) + xp_amount
    result = db.client.table("gamification_profiles").update({"total_xp": total, "level": _level_for_xp(total)}).eq("user_id", user_id).execute()
    return {"awarded": True, "xp_amount": xp_amount, "total_xp": total, "level": _level_for_xp(total), "profile": result.data[0] if result.data else None}


def _award_eligible_badges(user_id: int, profile: dict, problem: dict):
    """Evaluate badge rules after an accepted event; user_badges is unique."""
    badge_rows = db.client.table("badges").select("*").execute().data or []
    earned_rows = db.client.table("user_badges").select("badge_id").eq("user_id", user_id).execute().data or []
    earned_ids = {row.get("badge_id") for row in earned_rows}
    accepted = db.client.table("submissions").select("id").eq("user_id", user_id).eq("status", "accepted").execute().data or []
    bug_labs = db.client.table("submissions").select("id,problems(content_type)").eq("user_id", user_id).eq("status", "accepted").execute().data or []
    bug_labs_count = sum(1 for row in bug_labs if (row.get("problems") or {}).get("content_type") == "bug_lab")
    values = {
        "accepted_submissions": len(accepted),
        "streak_days": int(profile.get("current_streak") or 0),
        "total_xp": int(profile.get("total_xp") or 0),
        "bug_labs": bug_labs_count,
    }
    newly_earned = []
    for badge in badge_rows:
        badge_id = badge.get("id")
        condition = badge.get("condition_type")
        if badge_id in earned_ids or values.get(condition, 0) < int(badge.get("condition_value") or 1):
            continue
        inserted = db.client.table("user_badges").upsert({"user_id": user_id, "badge_id": badge_id}, on_conflict="user_id,badge_id").execute()
        earned = inserted.data[0] if inserted.data else {"user_id": user_id, "badge_id": badge_id}
        newly_earned.append({"badge": badge, "earned": earned})
        bonus = int(badge.get("xp_reward") or 0)
        if bonus:
            award_xp(user_id, f"badge:{badge_id}", "badge_earned", bonus, badge_id, {"badge_slug": badge.get("slug")})
    return newly_earned


def award_submission_rewards(user_id: int, submission_id: int, problem: dict, results: dict):
    """Reward only a fully accepted submission; retries remain idempotent."""
    if results.get("status") != "accepted":
        return {"awarded": False, "reason": "submission_not_accepted"}
    xp_amount = int(problem.get("xp_reward") or 80)
    reward = award_xp(user_id, f"submission:{submission_id}", "accepted_submission", xp_amount, submission_id, {"problem_id": problem.get("id")})
    streak = record_activity(user_id, "accepted_submission", submission_id)
    profile = reward.get("profile") or _profile(user_id) or streak
    badges = _award_eligible_badges(user_id, profile, problem)
    return {"awarded": reward.get("awarded", False), "xp": reward, "streak": streak, "badges": badges}


def get_summary(user_id: int):
    profile = _ensure_profile(user_id)
    badges = db.client.table("user_badges").select("earned_at,badges(slug,title,description)").eq("user_id", user_id).execute()
    return {"profile": profile, "badges": badges.data or []}
