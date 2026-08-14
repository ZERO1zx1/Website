#!/usr/bin/env bash
set -Eeuo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

export PYTHONPATH="${PYTHONPATH:-.}"
export FLASK_ENV="${FLASK_ENV:-testing}"
export FRONTEND_ONLY="${FRONTEND_ONLY:-false}"
export SECRET_KEY="${SECRET_KEY:-ci-test-secret}"

step() {
  printf '\n==> %s\n' "$1"
}

step "Compile Python"
python3 -m compileall -q .

step "Run pytest"
python3 -m pytest -q

step "Validate JavaScript syntax"
node --check frontend/static/js/app.js
node --check frontend/static/js/adapters/api-adapter.js
node --check frontend/static/js/i18n/translations.js
node --check frontend/static/js/pages/auth.js
node --check frontend/static/js/modules/monaco-editor.js

step "Validate frontend structure"
python3 ci/validate_frontend_structure.py

step "Validate workflow contract"
python3 ci/validate_workflow.py

step "Validate Compose topology"
python3 scripts/validate_compose_contract.py

step "Check repository hygiene"
git diff --check
if find . -path './.git' -prune -o -name '.env' -print | grep -q .; then
  echo 'A populated .env file must not be committed.' >&2
  exit 1
fi
if git grep -nE 'change-this-in-production|sk-[A-Za-z0-9]{20,}|service_role' -- ':!.github/**' ':!ci/**' ':!scripts/validate_compose_contract.py' ':!.env.example'; then
  echo 'Potential committed secret or insecure production default detected.' >&2
  exit 1
fi

printf '\nCI checks passed.\n'
