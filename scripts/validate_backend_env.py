"""Validate the local backend prerequisites without printing secret values."""

import os
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")


def check_supabase() -> dict:
    url = os.getenv("SUPABASE_URL", "").rstrip("/")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        return {
            "configured": False,
            "http_status": "not_configured",
            "schema_status": "not_configured",
        }

    headers = {"apikey": key, "Authorization": f"Bearer {key}"}
    try:
        response = requests.get(
            f"{url}/rest/v1/users",
            params={"select": "id", "limit": "1"},
            headers=headers,
            timeout=15,
        )
        schema_response = requests.get(
            f"{url}/rest/v1/users",
            params={"select": "id,password_hash,requested_role,teacher_approval_status", "limit": "1"},
            headers=headers,
            timeout=15,
        )
        return {
            "configured": True,
            "http_status": response.status_code,
            "schema_status": schema_response.status_code,
        }
    except requests.RequestException as error:
        return {"configured": True, "http_status": f"request_error:{type(error).__name__}", "schema_status": "unreachable"}


def check_sandbox() -> dict:
    sandbox_url = os.getenv("SANDBOX_URL", "").rstrip("/")
    if not sandbox_url:
        return {"configured": False, "health_status": "not_configured"}
    headers = {}
    if os.getenv("SANDBOX_TOKEN"):
        headers["X-Sandbox-Token"] = os.environ["SANDBOX_TOKEN"]
    try:
        response = requests.get(f"{sandbox_url}/health", headers=headers, timeout=5)
        return {"configured": True, "health_status": response.status_code}
    except requests.RequestException as error:
        return {"configured": True, "health_status": f"request_error:{type(error).__name__}"}


from app import create_app  # noqa: E402

app = create_app()
health_status = app.test_client().get("/api/health").status_code
supabase = check_supabase()
sandbox = check_sandbox()

print(f"flask_app_initialized={health_status == 200}")
print(f"supabase_configured={supabase['configured']}")
print(f"supabase_http_status={supabase['http_status']}")
print(f"auth_schema_status={supabase['schema_status']}")
print(f"auth_schema_ready={supabase['schema_status'] == 200}")
print(f"sandbox_configured={sandbox['configured']}")
print(f"sandbox_health_status={sandbox['health_status']}")
print(f"sandbox_ready={sandbox['health_status'] == 200}")
