from datetime import datetime, timedelta, timezone

import jwt
import pytest

from app import create_app
from backend.api import auth, learning


class FakeDB:
    user = {"id": 7, "auth_user_id": "11111111-1111-1111-1111-111111111111", "role": "student"}

    def get_user(self, user_id):
        return self.user if int(user_id) == 7 else None

    def get_profile(self, user_id):
        return {"id": user_id, "display_name": "Learner", "role": "student"}

    def update_profile(self, user_id, changes):
        return {"id": user_id, "role": "student", **changes}

    def get_learning_progress(self, user_id):
        return {"course_progress": [], "lesson_progress": []}

    def upsert_course_progress(self, user_id, values):
        return {"user_id": user_id, **values}

    def create_quiz_attempt(self, user_id, values):
        return {"id": "attempt-id", "user_id": user_id, **values}


@pytest.fixture()
def client(monkeypatch):
    monkeypatch.setenv("SECRET_KEY", "test-secret-that-is-at-least-thirty-two-bytes")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    fake = FakeDB()
    monkeypatch.setattr(auth, "db", fake)
    monkeypatch.setattr(learning, "db", fake)
    app = create_app("testing")
    app.config.update(TESTING=True)
    token = jwt.encode(
        {"user_id": 7, "exp": datetime.now(timezone.utc) + timedelta(minutes=5)},
        "test-secret-that-is-at-least-thirty-two-bytes",
        algorithm="HS256",
    )
    test_client = app.test_client()
    test_client.set_cookie("codecraft_session", token)
    return test_client


def test_profile_cannot_escalate_role(client):
    response = client.patch("/api/learning/profile", json={"role": "owner"})

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_request"


def test_profile_update_is_scoped_to_authenticated_identity(client):
    response = client.patch("/api/learning/profile", json={"display_name": "New name", "theme": "dark"})

    assert response.status_code == 200
    assert response.get_json()["profile"]["id"] == FakeDB.user["auth_user_id"]
    assert response.get_json()["profile"]["role"] == "student"


def test_course_progress_validation_and_identity_scope(client):
    invalid = client.put("/api/learning/progress", json={"course_slug": "python", "progress_percent": 101})
    valid = client.put("/api/learning/progress", json={"course_slug": "python", "progress_percent": 45})

    assert invalid.status_code == 400
    assert valid.status_code == 200
    assert valid.get_json()["course_progress"]["user_id"] == FakeDB.user["auth_user_id"]


def test_quiz_score_cannot_exceed_total(client):
    response = client.post(
        "/api/learning/quiz-attempts",
        json={
            "course_slug": "python",
            "lesson_slug": "variables",
            "score": 6,
            "total_questions": 5,
            "answers": [],
        },
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "invalid_score"
