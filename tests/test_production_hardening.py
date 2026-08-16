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


def test_local_backend_is_ready_without_supabase(monkeypatch, tmp_path):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "codehaven.sqlite3"))
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.setenv("SUBMISSION_QUEUE_MODE", "thread")

    response = create_app().test_client().get("/api/ready")

    assert response.status_code == 200
    assert response.get_json()["checks"]["database"] == "local_sqlite"


def test_local_authenticated_learning_flow(monkeypatch, tmp_path):
    from backend.db import db

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "flow.sqlite3"))
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    monkeypatch.setenv("SUBMISSION_QUEUE_MODE", "thread")
    db._client = None

    client = create_app().test_client()
    registered = client.post("/api/auth/register", json={"name": "Flow Learner", "email": "flow@example.com", "password": "password123"})
    assert registered.status_code == 201
    token = registered.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}

    assert client.get("/api/auth/me", headers=headers).status_code == 200
    courses = client.get("/api/courses", headers=headers)
    problems = client.get("/api/problems", headers=headers)
    dashboard = client.get("/api/analytics/dashboard", headers=headers)
    assert courses.status_code == 200 and len(courses.get_json()["courses"]) >= 3
    assert problems.status_code == 200 and len(problems.get_json()["problems"]) >= 3
    assert dashboard.status_code == 200
    assert dashboard.get_json()["stats"]["overall_mastery"] == 0


def test_local_lesson_completion_updates_dashboard(monkeypatch, tmp_path):
    from backend.db import db

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "progress.sqlite3"))
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    db._client = None

    client = create_app().test_client()
    registered = client.post("/api/auth/register", json={"name": "Progress Learner", "email": "progress@example.com", "password": "password123"})
    token = registered.get_json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    course = client.get("/api/courses/1", headers=headers).get_json()["course"]
    lesson_id = course["modules"][0]["lessons"][0]["id"]

    completed = client.post(f"/api/courses/lessons/{lesson_id}/complete", headers=headers)
    dashboard = client.get("/api/analytics/dashboard", headers=headers)

    assert completed.status_code == 201
    assert dashboard.status_code == 200
    assert dashboard.get_json()["stats"]["study_minutes"] == 20
    assert dashboard.get_json()["stats"]["current_streak"] == 1


def test_http_sandbox_mode_does_not_initialize_docker(monkeypatch):
    from backend.services import code_executor

    monkeypatch.setenv("SANDBOX_URL", "http://sandbox:8080")
    monkeypatch.setattr(code_executor.docker, "from_env", lambda: pytest.fail("Docker should be lazy in HTTP sandbox mode"))

    executor = code_executor.CodeExecutor()

    assert executor.client is None


def test_local_seed_is_idempotent_for_test_cases(tmp_path):
    from backend.local_db import LocalDB

    path = tmp_path / "seed.sqlite3"
    first = LocalDB(str(path))
    first_counts = first.client.table("test_cases").select("*").execute().data
    first_exams = first.client.table("exams").select("*").execute().data
    second = LocalDB(str(path))
    second_counts = second.client.table("test_cases").select("*").execute().data
    second_exams = second.client.table("exams").select("*").execute().data

    assert len(first_counts) == 4
    assert len(second_counts) == 4
    assert len(first_exams) == 1
    assert len(second_exams) == 1


def test_course_status_is_user_owned_and_realtime(monkeypatch, tmp_path):
    from backend.db import db

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "status.sqlite3"))
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    db._client = None

    client = create_app().test_client()
    first = client.post("/api/auth/register", json={"name": "First Learner", "email": "first@example.com", "password": "password123"})
    second = client.post("/api/auth/register", json={"name": "Second Learner", "email": "second@example.com", "password": "password123"})
    first_headers = {"Authorization": f"Bearer {first.get_json()['token']}"}
    second_headers = {"Authorization": f"Bearer {second.get_json()['token']}"}

    first_course = client.get("/api/courses/1", headers=first_headers).get_json()["course"]
    second_course = client.get("/api/courses/1", headers=second_headers).get_json()["course"]
    lesson_id = first_course["modules"][0]["lessons"][0]["id"]
    assert first_course["progress"] == 0
    assert second_course["progress"] == 0
    assert first_course["modules"][0]["lessons"][0]["status"] == "not_started"
    assert second_course["modules"][0]["lessons"][0]["status"] == "not_started"

    started = client.post(f"/api/courses/lessons/{lesson_id}/start", headers=first_headers)
    assert started.status_code == 200
    completed = client.post(f"/api/courses/lessons/{lesson_id}/complete", headers=first_headers)
    assert completed.status_code == 201

    first_after = client.get("/api/courses/1", headers=first_headers).get_json()["course"]
    second_after = client.get("/api/courses/1", headers=second_headers).get_json()["course"]
    assert first_after["progress"] == 50
    assert first_after["modules"][0]["status"] == "completed"
    assert first_after["modules"][0]["lessons"][0]["status"] == "completed"
    assert second_after["progress"] == 0
    assert second_after["modules"][0]["lessons"][0]["status"] == "not_started"



def test_public_multi_page_routes_render(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    from backend.db import db
    db._client = None
    client = create_app().test_client()
    for path, marker in [
        ("/", b"Start learning free"),
        ("/home", b"Start learning free"),
        ("/login", b"Forgot password?"),
        ("/register", b"Join Codehaven"),
        ("/password-reset", b"Reset your password."),
        ("/dashboard", b"YOUR WORKSPACE"),
    ]:
        response = client.get(path)
        assert response.status_code == 200
        assert marker in response.data


def test_standalone_workspace_pages_render_separately(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    from backend.db import db
    db._client = None
    client = create_app().test_client()
    for path, marker in [
        ("/learn", b'id="learn-view"'),
        ("/courses", b'id="learn-view"'),
        ("/practice", b'id="practice-view"'),
        ("/assessments", b'id="assessments-view"'),
        ("/exams", b'id="assessments-view"'),
        ("/profile", b'id="profile-view"'),
        ("/settings", b'id="settings-view"'),
    ]:
        response = client.get(path)
        assert response.status_code == 200
        assert marker in response.data
        assert b'workspace_base.html' not in response.data
        assert b'frontend/static/js/app.js' not in response.data
        assert b'id="primary-navigation"' in response.data


def test_local_password_reset_request_and_confirm(monkeypatch, tmp_path):
    from backend.db import db
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "reset.sqlite3"))
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    db._client = None
    client = create_app().test_client()
    registered = client.post("/api/auth/register", json={"name": "Reset Learner", "email": "reset@example.com", "password": "oldpassword"})
    assert registered.status_code == 201
    requested = client.post("/api/auth/password-reset/request", json={"email": "reset@example.com"})
    assert requested.status_code == 200
    reset_url = requested.get_json()["reset_url"]
    token = reset_url.split("token=", 1)[1]
    confirmed = client.post("/api/auth/password-reset/confirm", json={"token": token, "password": "newpassword"})
    assert confirmed.status_code == 200
    login = client.post("/api/auth/login", json={"email": "reset@example.com", "password": "newpassword"})
    assert login.status_code == 200
    reused = client.post("/api/auth/password-reset/confirm", json={"token": token, "password": "thirdpassword"})
    assert reused.status_code == 400



def test_register_page_contains_client_validation_contract(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    from backend.db import db
    db._client = None
    html = create_app().test_client().get("/register").data
    assert b"data-validation-summary" in html
    assert b"data-field-error=\"terms\"" in html
    assert b"novalidate" in html


def test_dashboard_returns_authenticated_user_profile(monkeypatch, tmp_path):
    from backend.db import db
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "dashboard-user.sqlite3"))
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    db._client = None
    client = create_app().test_client()
    registered = client.post("/api/auth/register", json={"name": "Dashboard User", "email": "dashboard@example.com", "password": "password123"})
    token = registered.get_json()["token"]
    response = client.get("/api/analytics/dashboard", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.get_json()["user"]["name"] == "Dashboard User"
    assert response.get_json()["user"]["role"] == "student"



def test_dashboard_workspace_uses_live_discovery_markers(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    from backend.db import db
    db._client = None
    html = create_app().test_client().get("/workspace").data
    assert b"dashboard-course-grid" in html
    assert b"sidebar-up-next-title" in html
    assert b"Build your first API" not in html



def test_local_exam_attempt_grading_and_progress_report(monkeypatch, tmp_path):
    from backend.db import db

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "exam-flow.sqlite3"))
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    db._client = None
    client = create_app().test_client()
    registered = client.post("/api/auth/register", json={"name": "Exam Learner", "email": "exam@example.com", "password": "password123"})
    headers = {"Authorization": f"Bearer {registered.get_json()['token']}"}

    exams = client.get("/api/exams", headers=headers)
    assert exams.status_code == 200
    exam = exams.get_json()["exams"][0]
    detail = client.get(f"/api/exams/{exam['id']}", headers=headers)
    assert detail.status_code == 200
    assert "correct_answer" not in detail.get_json()["exam"]["questions"][0]

    started = client.post(f"/api/exams/{exam['id']}/attempts", headers=headers)
    assert started.status_code == 201
    attempt = started.get_json()["attempt"]
    for question, answer in zip(attempt["exam"]["questions"], ["tuple", "None", "len"]):
        saved = client.patch(f"/api/exams/attempts/{attempt['id']}/answers/{question['id']}", json={"answer": answer}, headers=headers)
        assert saved.status_code == 200
    submitted = client.post(f"/api/exams/attempts/{attempt['id']}/submit", headers=headers)
    assert submitted.status_code == 200
    submitted_attempt = submitted.get_json()["attempt"]
    assert submitted_attempt["score"] == 100.0
    assert "correct_answer" not in submitted_attempt["exam"]["questions"][0]
    assert bool(submitted_attempt["result_answers"][0]["is_correct"]) is True

    report = client.get("/api/analytics/progress-report", headers=headers)
    assert report.status_code == 200
    assert report.get_json()["report"]["exams"][0]["score"] == 100.0
    dashboard = client.get("/api/analytics/dashboard", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.get_json()["exam_summary"]["best_score"] == 100.0


def test_exam_builder_permission_and_attempt_ownership(monkeypatch, tmp_path):
    from backend.db import db

    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("LOCAL_DB_PATH", str(tmp_path / "exam-owner.sqlite3"))
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    db._client = None
    client = create_app().test_client()
    teacher = client.post("/api/auth/register", json={"name": "Exam Teacher", "email": "teacher@example.com", "password": "password123"})
    student = client.post("/api/auth/register", json={"name": "Exam Student", "email": "student@example.com", "password": "password123"})
    teacher_id = teacher.get_json()["user"]["id"]
    db.update_user(teacher_id, {"role": "teacher", "requested_role": None, "teacher_approval_status": "approved"})
    teacher_headers = {"Authorization": f"Bearer {teacher.get_json()['token']}"}
    student_headers = {"Authorization": f"Bearer {student.get_json()['token']}"}
    payload = {"title": "Teacher checkpoint", "duration_minutes": 10, "max_attempts": 2, "questions": [{"question_type": "multiple_choice", "prompt": "What is 2 + 2?", "options": ["3", "4"], "correct_answer": "4", "points": 1}]}
    created = client.post("/api/exams", json=payload, headers=teacher_headers)
    assert created.status_code == 201
    exam_id = created.get_json()["exam"]["id"]
    assert client.post("/api/exams", json=payload, headers=student_headers).status_code == 403
    started = client.post(f"/api/exams/{exam_id}/attempts", headers=student_headers)
    assert started.status_code == 201
    attempt_id = started.get_json()["attempt"]["id"]
    assert client.get(f"/api/exams/attempts/{attempt_id}", headers=teacher_headers).status_code == 200
    assert client.get(f"/api/exams/attempts/{attempt_id}", headers=student_headers).status_code == 200



def test_assessment_workspace_contains_training_views(monkeypatch):
    monkeypatch.setenv("FLASK_ENV", "development")
    monkeypatch.setenv("FRONTEND_ONLY", "false")
    monkeypatch.setenv("LOCAL_DB", "true")
    monkeypatch.setenv("SECRET_KEY", "local-development-secret-that-is-long-enough")
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.delenv("SUPABASE_KEY", raising=False)
    from backend.db import db
    db._client = None
    html = create_app().test_client().get("/assessments").data
    assert b"exam-builder-form" in html
    assert b"student-exam-view" in html
    assert b"teacher-exam-report" in html
