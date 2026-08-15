#!/usr/bin/env python3
"""Validate the canonical Flask frontend layout used by local and CI checks."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = {
    "frontend/templates/index.html",
    "frontend/templates/pages/base.html",
    "frontend/templates/pages/home.html",
    "frontend/templates/pages/login.html",
    "frontend/templates/pages/register.html",
    "frontend/templates/pages/password_reset.html",
    "frontend/templates/pages/dashboard.html",
    "frontend/templates/pages/workspace_base.html",
    "frontend/templates/pages/workspace_dashboard.html",
    "frontend/templates/pages/learn.html",
    "frontend/templates/pages/practice.html",
    "frontend/templates/pages/assessments.html",
    "frontend/templates/pages/profile.html",
    "frontend/templates/pages/settings.html",
    "frontend/static/css/style.css",
    "frontend/static/css/site/site.css",
    "frontend/static/js/app.js",
    "frontend/static/js/pages/auth.js",
    "frontend/static/js/adapters/api-adapter.js",
    "frontend/static/js/i18n/translations.js",
    "frontend/static/js/modules/monaco-editor.js",
    "frontend/static/assets/README.md",
}
REQUIRED_DIRS = {
    "frontend/static/assets/images",
    "frontend/static/assets/icons",
    "frontend/static/assets/fonts",
    "frontend/static/css/workspace",
}


def main() -> int:
    missing_files = sorted(path for path in REQUIRED_FILES if not (ROOT / path).is_file())
    missing_dirs = sorted(path for path in REQUIRED_DIRS if not (ROOT / path).is_dir())
    if missing_files or missing_dirs:
        if missing_files:
            print("Missing frontend files:", *missing_files, sep="\n- ", file=sys.stderr)
        if missing_dirs:
            print("Missing frontend directories:", *missing_dirs, sep="\n- ", file=sys.stderr)
        return 1
    print(f"frontend_structure=ok files={len(REQUIRED_FILES)} directories={len(REQUIRED_DIRS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
