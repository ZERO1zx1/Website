import json

import pytest

from app import create_app
from backend.services import submission_queue


def test_production_requires_backend_configuration(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "production")
    monkeypatch.setenv("SECRET_KEY", "a-long-production-secret")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.delenv("SANDBOX_URL", raising=False)
    monkeypatch.setenv("SUBMISSION_QUEUE_MODE", "thread")

    with pytest.raises(RuntimeError, match="SUPABASE_URL"):
        create_app()


def test_readiness_reports_sandbox_token_missing(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("SECRET_KEY", "test-secret")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_KEY", "test-key")
    monkeypatch.setenv("SANDBOX_URL", "http://sandbox:8080")
    monkeypatch.delenv("SANDBOX_TOKEN", raising=False)
    monkeypatch.setenv("SUBMISSION_QUEUE_MODE", "thread")

    response = create_app().test_client().get("/api/ready")

    assert response.status_code == 503
    assert "SANDBOX_TOKEN" in response.get_json()["missing"]


def test_queue_discards_malformed_payload(monkeypatch):
    class FakeRedis:
        def blpop(self, name, timeout):
            return (name, json.dumps({"submission_id": "not-an-int"}))

    monkeypatch.setattr(submission_queue, "_redis", lambda: FakeRedis())

    assert submission_queue.process_next_redis_submission(timeout=0) is True


def test_queue_marks_submission_failed_when_redis_enqueue_fails(monkeypatch):
    class BrokenRedis:
        def rpush(self, name, payload):
            raise RuntimeError("redis unavailable")

    calls = []
    monkeypatch.setenv("SUBMISSION_QUEUE_MODE", "redis")
    monkeypatch.setattr(submission_queue, "_redis", lambda: BrokenRedis())
    monkeypatch.setattr(
        submission_queue.db,
        "update_submission_status",
        lambda submission_id, status, score=None: calls.append((submission_id, status, score)),
    )

    with pytest.raises(RuntimeError, match="redis unavailable"):
        submission_queue.enqueue_submission(12, 4, 7, "print(1)")

    assert calls == [(12, "error", 0)]


def test_hidden_submission_results_are_redacted_for_students():
    from backend.api.submissions import _result_payload

    payload = _result_payload(
        [{
            "test_number": 2,
            "passed": False,
            "actual_output": "wrong",
            "expected_output": "secret-answer",
            "input": "secret-input",
            "is_hidden": True,
        }],
        {"id": 10, "role": "student"},
    )

    assert payload == [{"test_number": 2, "passed": False, "actual_output": "wrong"}]


def test_hidden_submission_results_are_visible_only_to_staff():
    from backend.api.submissions import _result_payload

    result = {"test_number": 2, "expected_output": "secret-answer", "is_hidden": True}
    assert _result_payload([result], {"id": 1, "role": "teacher"}) == [result]


def test_sandbox_requires_token_by_default(monkeypatch):
    import sandbox.service as sandbox_service

    monkeypatch.delenv("SANDBOX_REQUIRE_TOKEN", raising=False)
    monkeypatch.delenv("SANDBOX_ALLOW_INSECURE", raising=False)
    assert sandbox_service._token_is_required() is True


def test_sandbox_insecure_bypass_requires_explicit_opt_in(monkeypatch):
    import sandbox.service as sandbox_service

    monkeypatch.delenv("SANDBOX_REQUIRE_TOKEN", raising=False)
    monkeypatch.setenv("SANDBOX_ALLOW_INSECURE", "true")
    assert sandbox_service._token_is_required() is False
