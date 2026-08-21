"""Build a JSON request file for the reviewed CodeCraft Supabase migration."""
from pathlib import Path
import json

project_root = Path(__file__).resolve().parents[1]
sql_path = project_root / "supabase" / "migrations" / "20260821_codecraft_auth_progress.sql"
output_path = project_root / "supabase" / "migrations" / "20260821_codecraft_auth_progress.input.json"

payload = {
    "project_id": "rqalizeohjpwtvepltqe",
    "name": "codecraft_auth_progress",
    "query": sql_path.read_text(encoding="utf-8"),
}
output_path.write_text(json.dumps(payload), encoding="utf-8")
print(output_path)
