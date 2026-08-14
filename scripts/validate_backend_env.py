import os
from pathlib import Path

import requests
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

url = os.environ["SUPABASE_URL"].rstrip("/")
key = os.environ["SUPABASE_KEY"]

from app import create_app  # noqa: E402

app = create_app()
health_status = app.test_client().get("/api/health").status_code
headers = {
    "apikey": key,
    "Authorization": f"Bearer {key}",
}
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

print(f"flask_app_initialized={health_status == 200}")
print(f"supabase_http_status={response.status_code}")
print(f"supabase_request_reached={response.status_code not in {0, 502, 503, 504}}")
print(f"auth_schema_status={schema_response.status_code}")
print(f"auth_schema_ready={schema_response.status_code == 200}")
