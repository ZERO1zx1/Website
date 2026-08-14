"""Submission queue with local development and Redis worker modes."""

from concurrent.futures import Future, ThreadPoolExecutor
import json
import logging
import os
from typing import Optional

from backend.db import db
from backend.services.submission_evaluator import get_processor

logger = logging.getLogger(__name__)
_QUEUE_NAME = os.getenv("SUBMISSION_QUEUE_NAME", "codehaven:submissions")
_MAX_WORKERS = max(1, int(os.getenv("SUBMISSION_WORKERS", "2")))
_executor = ThreadPoolExecutor(max_workers=_MAX_WORKERS, thread_name_prefix="submission")
_redis_client = None


def _queue_mode() -> str:
    return os.getenv("SUBMISSION_QUEUE_MODE", "thread").lower()


def _mark_submission_error(submission_id: int) -> None:
    try:
        db.update_submission_status(submission_id, "error", 0)
    except Exception:
        logger.exception("Unable to mark submission %s as failed", submission_id)


def _process_submission(submission_id: int, user_id: int, problem_id: int, code: str, language: str) -> None:
    try:
        get_processor().process_submission(
            submission_id=submission_id,
            user_id=user_id,
            problem_id=problem_id,
            code=code,
            language=language,
        )
    except Exception:
        logger.exception("Unhandled submission worker failure for %s", submission_id)
        _mark_submission_error(submission_id)


def _redis():
    global _redis_client
    if _redis_client is None:
        import redis

        _redis_client = redis.from_url(
            os.getenv("REDIS_URL", "redis://localhost:6379/0"),
            decode_responses=True,
            socket_connect_timeout=5,
            socket_timeout=10,
        )
    return _redis_client


def enqueue_submission(
    submission_id: int,
    user_id: int,
    problem_id: int,
    code: str,
    language: str = "python",
) -> Optional[Future]:
    """Queue a submission; Redis mode is used by the production worker stack."""
    payload = {
        "submission_id": submission_id,
        "user_id": user_id,
        "problem_id": problem_id,
        "code": code,
        "language": language,
    }
    if _queue_mode() == "redis":
        try:
            _redis().rpush(_QUEUE_NAME, json.dumps(payload))
        except Exception:
            logger.exception("Unable to enqueue submission %s", submission_id)
            _mark_submission_error(submission_id)
            raise
        return None
    return _executor.submit(_process_submission, submission_id, user_id, problem_id, code, language)


def process_next_redis_submission(timeout: int = 5) -> bool:
    """Process one Redis queue item; return False when the worker should poll again."""
    item = _redis().blpop(_QUEUE_NAME, timeout=timeout)
    if not item:
        return False
    _, raw_payload = item
    try:
        payload = json.loads(raw_payload)
        submission_id = int(payload["submission_id"])
        user_id = int(payload["user_id"])
        problem_id = int(payload["problem_id"])
        code = payload["code"]
        language = str(payload.get("language", "python"))
        if not isinstance(code, str) or not code.strip():
            raise ValueError("submission code is missing")
    except (TypeError, ValueError, KeyError, json.JSONDecodeError):
        logger.error("Discarding malformed submission queue payload")
        return True

    _process_submission(submission_id, user_id, problem_id, code, language)
    return True


def shutdown_submission_queue(wait: bool = True) -> None:
    """Stop the in-process worker pool during controlled application shutdown."""
    _executor.shutdown(wait=wait, cancel_futures=not wait)
