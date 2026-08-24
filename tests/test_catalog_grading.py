from datetime import datetime, timedelta, timezone

import jwt

from app import create_app
from backend.api import auth, submissions


class FakeAuthDB:
    def get_user(self, user_id):
        return {"id": 7, "auth_user_id": "11111111-1111-1111-1111-111111111111", "role": "student"} if int(user_id) == 7 else None


class FakeExecutor:
    def execute_test_cases(self, *, code, language, test_cases):
        return {
            "status": "accepted",
            "total_tests": len(test_cases),
            "passed_tests": len(test_cases),
            "failed_tests": 0,
            "test_results": [],
            "language_seen": language,
        }


def make_client(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-that-is-at-least-thirty-two-bytes")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("SANDBOX_URL", "http://sandbox.test")
    monkeypatch.setattr(auth, "db", FakeAuthDB())
    monkeypatch.setattr(submissions, "get_executor", lambda: FakeExecutor())
    app = create_app("testing")
    app.config.update(TESTING=True)
    token = jwt.encode(
        {"user_id": 7, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "test-secret-that-is-at-least-thirty-two-bytes",
        algorithm="HS256",
    )
    client = app.test_client()
    client.set_cookie("codecraft_session", token)
    return client


def test_catalog_challenge_run_uses_challenge_tests(monkeypatch):
    client = make_client(monkeypatch)

    response = client.post(
        "/api/submissions/run",
        json={"challenge_id": "js-safe-dom", "language": "javascript", "code": "output.textContent = name;"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "catalog"
    assert payload["challenge_id"] == "js-safe-dom"
    assert payload["language_seen"] == "javascript"
    assert payload["total_tests"] == 1


def test_catalog_challenge_run_supports_static_html(monkeypatch):
    client = make_client(monkeypatch)

    response = client.post(
        "/api/submissions/run",
        json={"challenge_id": "html-navigation", "language": "html", "code": "<nav aria-label=\"Цэс\"></nav>"},
    )

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["mode"] == "catalog"
    assert payload["language_seen"] == "html"
    assert payload["total_tests"] == 1
