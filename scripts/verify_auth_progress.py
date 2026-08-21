"""Non-destructive local verification for CodeCraft Supabase Auth and progress APIs."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
BASE_URL = os.getenv("CODECRAFT_TEST_BASE_URL", "http://127.0.0.1:5004").rstrip("/")


def check(condition: bool, label: str) -> None:
    if not condition:
        raise AssertionError(label)
    print(f"PASS: {label}")


def main() -> int:
    ready = requests.get(f"{BASE_URL}/api/ready", timeout=10)
    check(ready.status_code == 200 and ready.json().get("mode") == "backend", "Flask backend readiness")

    google_start = requests.get(f"{BASE_URL}/api/auth/google/start", timeout=10)
    google_payload = google_start.json()
    check(google_start.status_code == 200 and google_payload.get("url", "").startswith("https://"), "Google OAuth authorization URL")

    invalid_register = requests.post(f"{BASE_URL}/api/auth/register", json={}, timeout=10)
    check(invalid_register.status_code == 400, "Email/password registration validation")

    protected_progress = requests.get(f"{BASE_URL}/api/progress", timeout=10)
    check(protected_progress.status_code == 401, "Progress API rejects unauthenticated access")

    settings = requests.get(
        f"{os.environ['SUPABASE_URL'].rstrip('/')}/auth/v1/settings",
        headers={"apikey": os.environ["SUPABASE_KEY"]},
        timeout=15,
    )
    check(settings.status_code == 200, "Supabase Auth settings reachable")
    external = settings.json().get("external", {})
    google_enabled = external.get("google")
    check(bool(google_enabled), "Supabase Google provider enabled")

    # The service role is tested only for an empty, limited schema request; no learner data is printed.
    schema_probe = requests.get(
        f"{os.environ['SUPABASE_URL'].rstrip('/')}/rest/v1/profiles?select=id&limit=1",
        headers={"apikey": os.environ["SUPABASE_SERVICE_ROLE_KEY"], "Authorization": f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}"},
        timeout=15,
    )
    check(schema_probe.status_code == 200, "Supabase profiles table reachable")

    print("AUTH_PROGRESS_VERIFICATION_OK")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f"AUTH_PROGRESS_VERIFICATION_FAILED: {exc}", file=sys.stderr)
        raise SystemExit(1)
