"""Create a temporary non-personal Auth user via Admin API, verify CodeCraft progress, then delete it."""
from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
BASE_URL = os.getenv("CODECRAFT_TEST_BASE_URL", "http://127.0.0.1:5004").rstrip("/")
SUPABASE_URL = os.environ["SUPABASE_URL"].rstrip("/")
SERVICE_KEY = os.environ["SUPABASE_SERVICE_ROLE_KEY"]
HEADERS = {"apikey": SERVICE_KEY, "Authorization": f"Bearer {SERVICE_KEY}", "Content-Type": "application/json"}


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"PASS: {label}")


def main() -> int:
    nonce = secrets.token_hex(8)
    email = f"codecraft.integration.{nonce}@example.com"
    password = f"CodeCraft!{secrets.token_urlsafe(12)}"
    user_id = None
    try:
        # Create directly via Admin API to bypass public email rate limits
        create = requests.post(
            f"{SUPABASE_URL}/auth/v1/admin/users",
            headers=HEADERS,
            json={"email": email, "password": password, "email_confirm": True, "user_metadata": {"display_name": "CodeCraft Integration"}},
            timeout=20,
        )
        if create.status_code not in {200, 201}:
            print(f"CREATE_USER_STATUS={create.status_code} BODY={create.text[:300]}", file=sys.stderr)
        check(create.status_code in {200, 201}, "Temporary Supabase Auth user created via Admin API")
        user_id = create.json()["id"]
        
        login = requests.post(f"{BASE_URL}/api/auth/login", json={"email": email, "password": password}, timeout=20)
        check(login.status_code == 200, "Email/password login returns a session")
        session = login.json()
        check(bool(session.get("token")) and session.get("user", {}).get("id") == user_id, "Supabase access token and profile returned")
        learner_headers = {"Authorization": f"Bearer {session['token']}"}

        profile = requests.get(f"{BASE_URL}/api/progress/profile", headers=learner_headers, timeout=20)
        check(profile.status_code == 200 and profile.json()["profile"]["email"] == email, "Profile is automatically provisioned via Auth trigger")

        initial = requests.get(f"{BASE_URL}/api/progress", headers=learner_headers, timeout=20)
        check(initial.status_code == 200 and initial.json()["completed_lessons"] == 0, "Empty initial learner progress")

        completed = requests.post(
            f"{BASE_URL}/api/progress/lessons",
            headers=learner_headers,
            json={"course_id": "python", "lesson_id": "py-start"},
            timeout=20,
        )
        check(completed.status_code == 200, "Lesson completion is persisted via RLS")
        summary = completed.json()["summary"]
        check("python:py-start" in summary["completed_lesson_keys"], "Persisted lesson appears in learner summary")

        removed = requests.delete(f"{BASE_URL}/api/progress/lessons/python/py-start", headers=learner_headers, timeout=20)
        check(removed.status_code == 200 and "python:py-start" not in removed.json()["summary"]["completed_lesson_keys"], "Lesson completion can be removed via RLS")

        print("AUTH_PROGRESS_INTEGRATION_OK")
        return 0
    finally:
        if user_id:
            deleted = requests.delete(f"{SUPABASE_URL}/auth/v1/admin/users/{user_id}", headers=HEADERS, timeout=20)
            if deleted.status_code not in {200, 204}:
                print("WARNING: Temporary test user cleanup needs manual review.", file=sys.stderr)
            else:
                print("CLEANUP: Temporary test user deleted")


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"AUTH_PROGRESS_INTEGRATION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
