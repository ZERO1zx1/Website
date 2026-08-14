"""Run the shared Redis-backed submission evaluator worker."""

import logging
import os
import signal

from backend.services.submission_queue import process_next_redis_submission

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
_STOP = False


def _stop(*_args):
    global _STOP
    _STOP = True


signal.signal(signal.SIGTERM, _stop)
signal.signal(signal.SIGINT, _stop)


if __name__ == "__main__":
    if os.getenv("SUBMISSION_QUEUE_MODE", "redis").lower() != "redis":
        raise SystemExit("SUBMISSION_QUEUE_MODE must be redis for the worker process")
    while not _STOP:
        process_next_redis_submission(timeout=5)
