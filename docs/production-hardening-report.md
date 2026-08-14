# Production Hardening Report

## Current latest commit audited

The implementation started from `7793b87`, `Merge pull request #2 from ZERO1zx1/fix/frontend-complete`, on the repository’s latest `main` branch. The completed work is on branch `fix/production-hardening` in commit `1857287`, `harden production runtime and full-stack integration`.

## Critical failures found and fixed

| Area | Verified issue | Resolution |
|---|---|---|
| Docker networking | Web and worker were attached only to an internal network, which could block Supabase access. | Added `app_network` for external services and retained `sandbox_internal` for Redis and sandbox traffic. |
| Sandbox secrets | Compose used a known fallback token. | Removed the fallback and required `${SANDBOX_TOKEN:?SANDBOX_TOKEN must be set}`. |
| Sandbox startup | Empty tokens could make execution unauthenticated. | Sandbox authentication now fails closed by default; an insecure bypass requires explicit opt-in. |
| Queue reliability | Import-time queue mode, malformed payload crashes, and worker exceptions could leave submissions pending. | Queue mode is read at call time, malformed payloads are discarded safely, Redis enqueue failures are surfaced, and worker failures mark submissions as `error`. |
| Submission security | Students could receive hidden test expected output through result and SSE responses; Owner access was incomplete. | Hidden results are redacted for students, staff access includes Owner, and response errors are normalized. |
| Frontend live mode | Auth failures could silently switch authenticated users to fake data. | Backend-mode failures remain visible error/session states; demo fixtures are limited to explicit demo mode. |
| Browser requests | Requests lacked timeout handling and tokens remained in local storage. | Added abort timeouts, normalized unauthorized handling, migration from legacy local-storage tokens, and session-storage cleanup. |
| Duplicate submissions | Run and Submit controls could issue overlapping requests. | Added in-flight request locking and reliable button restoration. |
| Readiness | `/api/ready` reported configuration presence without service probes. | Added configuration, Supabase, Redis, and sandbox readiness checks with meaningful `503` responses. |
| Analytics | Generic dashboard required only the student permission and exposed raw exception text in several endpoints. | Made dashboard access role-aware and normalized analytics failures. |
| CI | No meaningful GitHub Actions verification existed. | Added CI for Python compilation/tests, JavaScript syntax, hygiene, Compose contract, and Compose config. |

## Docker verification

The repository now contains a permanent Compose contract check that validates the split network topology, absence of Redis/sandbox host ports, and removal of insecure token defaults. It passed locally with `compose_contract=ok`.

The real `docker compose config`, image build, and service startup could not be run in the current sandbox because Docker Engine is unavailable. GitHub Actions is configured to run `docker compose config` in CI, and the documented production run remains `docker compose up --build` after `.env` is populated.

## Supabase verification

Live Supabase end-to-end behavior was **not tested** because Supabase credentials were unavailable in the sandbox. The environment validator reported `supabase_configured=False` and `auth_schema_status=not_configured`. The migration order and seed path are documented as `001_auth_roles.sql`, `002_learning_platform.sql`, `003_external_auth_identities.sql`, then `backend/db/seed/001_demo_content.sql`.

## Security fixes

The sandbox is no longer permitted to run without an authentication token unless `SANDBOX_ALLOW_INSECURE=true` or an equivalent explicit configuration is provided. Production Compose does not publish Redis or the sandbox to the host, and the web and worker services have a route to external Supabase services.

Submission result and SSE paths now enforce ownership or staff authorization and remove hidden test input and expected output from student responses. Production configuration fails fast when required secrets are missing. The frontend removes legacy local-storage bearer tokens, uses session storage for the current session, clears expired sessions, and removes tokens from the URL fragment after OAuth consumption.

## Frontend/backend fixes

The frontend API adapter now covers authentication, dashboard, courses, problems, visible-test execution, graded submission, submission retrieval, and SSE/polling status. The browser uses `POST /api/submissions/run` for visible tests and `POST /api/submissions` for graded evaluation. Live errors render as explicit error states and are not replaced by mock statistics.

The existing Flask, HTML, CSS, JavaScript, Supabase, Redis, worker, and sandbox architecture was preserved. This was a hardening and integration pass rather than a framework migration or a second mock frontend.

## Tests and checks

| Command | Result |
|---|---|
| `python3 -m compileall -q .` | Passed |
| `PYTHONPATH=. pytest -q` | Passed: 34 tests |
| `node --check frontend/static/js/app.js` | Passed |
| `node --check frontend/static/js/adapters/api-adapter.js` | Passed |
| `node --check frontend/static/js/monaco-editor.js` | Passed |
| `node --check frontend/static/js/i18n/translations.js` | Passed |
| `PYTHONPATH=. python3 scripts/validate_compose_contract.py` | Passed |
| `git diff --check` | Passed |
| Frontend-only Flask root/health/readiness/static smoke test | Passed: HTTP 200 responses |
| Sandbox production health and missing-token smoke test | Passed: health 200, missing token 403 |
| `PYTHONPATH=. python3 scripts/validate_backend_env.py` | Ran; correctly reported external Supabase and sandbox configuration unavailable |
| `docker compose config` | Not run: Docker Engine unavailable |
| `docker compose build` | Not run: Docker Engine unavailable |
| Live Supabase E2E | Not run: credentials unavailable |

## Files changed

The main implementation changes are in `app.py`, `docker-compose.yml`, `sandbox/service.py`, `backend/services/submission_queue.py`, `backend/api/submissions.py`, `backend/api/analytics.py`, `frontend/static/js/adapters/api-adapter.js`, and `frontend/static/js/app.js`. Regression coverage is in `tests/test_production_hardening.py`. CI is in `.github/workflows/ci.yml`, and the Compose contract check is in `scripts/validate_compose_contract.py`.

Documentation was synchronized in `README.md`, `PROGRESS.md` was intentionally left as historical project progress, `frontend/README.md`, `docs/backend-integration.md`, `docs/frontend-design-handoff.md`, `.env.example`, and this report.

## Remaining limitations

The repository still requires real Supabase credentials, applied migrations and seed data, Docker Engine, and a deployment secret store for a genuine production run. The current frontend remains primarily a student workspace; the backend exposes teacher, admin, and owner capabilities, but a complete role-specific management UI is not implemented in this hardening pass. A pull request was not created automatically; the pushed branch is available for review at `https://github.com/ZERO1zx1/Website/tree/fix/production-hardening`.

## Git state

| Item | Value |
|---|---|
| Branch | `fix/production-hardening` |
| Commit | `1857287 harden production runtime and full-stack integration` |
| Remote branch | `origin/fix/production-hardening` |
| Pull request | Not created |
| Working tree | Clean after the final verification commit |


# Live local-backend upgrade — August 2026

The authenticated browser experience was upgraded so the visible site no longer offers a demo-learner continuation or labels the account shortcut as preview login. In development without Supabase credentials, Flask now uses a real file-backed SQLite database at `instance/codehaven.sqlite3` by default when no database mode is explicitly configured. `LOCAL_DB_PATH` can override the location, and the database file is ignored by Git.

The local backend seeds three courses, modules, lessons, skills, programming problems and test cases. Registration, login, current-user lookup, course catalog, course modules, problem library, dashboard statistics, and lesson completion now use persisted backend data. A new `lesson_progress` table and `004_learning_progress.sql` migration support production Supabase deployments.

The live browser verification used a real local test account (`Browser Learner`) and confirmed authenticated registration, dashboard loading, three backend courses, three backend problems, editor loading, lesson completion with HTTP 201, and dashboard refresh from `0m` to `20m` study time with a one-day streak. The browser also confirmed that the authenticated sidebar shows `Account` rather than `Preview login / register`.

The isolated code execution button correctly reports `Runtime execution is temporarily unavailable` in this environment because Docker/sandbox execution services are not available. This is an explicit safe failure rather than an unsafe in-process execution fallback. Production execution still requires the sandbox service and Docker Compose stack.
