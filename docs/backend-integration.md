# Backend integration plan

## Current boundary

The frontend is a plain HTML, CSS and JavaScript application rendered by Flask. It uses `mockAdapter` for preview mode and switches to the authenticated API adapter in normal backend mode. The backend is organized under `backend/` and remains available in normal Flask mode.

## API groups

| Group | Blueprint location | Prefix | Frontend consumer |
|---|---|---|---|
| Authentication | `backend/api/auth.py` | `/api/auth` | Login, register, current user, role |
| Courses | `backend/api/courses.py` | `/api/courses` | Learning path and modules |
| Problems | `backend/api/problems.py` | `/api/problems` | Practice library and filters |
| Submissions | `backend/api/submissions.py` | `/api/submissions` | Run/submit code and result status |
| Teacher | `backend/api/teacher.py` | `/api/teacher` | Teacher dashboard and class analytics |
| Analytics | `backend/api/analytics.py` | `/api/analytics` | Mastery, activity and skill map |

## Authentication schema prerequisite

Before enabling normal authentication, apply `backend/db/migrations/001_auth_roles.sql`. It adds `password_hash`, `requested_role` and `teacher_approval_status`, restricts role values to `owner`, `admin`, `teacher` and `student`, and adds an approval lookup index. Existing plaintext passwords must not be copied into `password_hash`; legacy accounts should complete a password reset before production login is enabled.

Apply `backend/db/seed/001_demo_content.sql` after the migrations when the project needs an initial student-facing catalog. It creates starter courses, modules, lessons, skills, Python problems and visible/hidden test cases without creating a fake user account.

After the auth migration, apply `backend/db/migrations/002_learning_platform.sql`. It creates the idempotent learning-platform tables required by courses, modules, lessons, classes, enrollments, skills, problems, test cases, hints, submissions, evaluator results, teacher feedback, exams and mastery analytics. The migration also adds foreign keys, uniqueness constraints, query indexes and `updated_at` triggers. Apply `backend/db/migrations/004_learning_progress.sql` after it to persist authenticated lesson completion. The application can run without sample content, but courses and problems must be seeded or created by a teacher before the authenticated learning screens contain live records.

Apply `backend/db/migrations/003_external_auth_identities.sql` to add the Supabase Auth identity link, provider name and avatar fields used by Gmail OTP and Google OAuth. In Supabase Auth, enable Email provider, configure the email template to include `{{ .Token }}` when a six-digit code is required, and add the configured `OTP_REDIRECT_URL` to the project redirect allow-list. Enable Google provider, set its Google client ID and client secret in Supabase Auth, and add `GOOGLE_OAUTH_REDIRECT_URL` to Supabase Auth URL Configuration. The Flask endpoints are `POST /api/auth/otp/request`, `POST /api/auth/otp/verify`, `GET /api/auth/google/start` and `GET /api/auth/google/callback`.

## Recommended integration order

Authentication is integrated first because all other screens need a current user and authorization state. In local development, omit Supabase credentials and Flask uses a file-backed SQLite database with seeded courses, modules, lessons, skills, problems and test cases. In Supabase deployments, apply migrations 001–004, verify password hashing and test owner/admin/teacher/student permissions, then use the login screen to establish the API session. The dashboard adapter consumes normalized mastery, lesson-progress, and recent-submission data; the learning path and problem library adapters consume `/api/courses` and `/api/problems`. Completing a lesson calls `POST /api/courses/lessons/<lesson_id>/complete` and refreshes persisted dashboard metrics. Submission integration is asynchronous: `POST /api/submissions` creates a pending row and queues the evaluator, while the frontend first attempts `GET /api/submissions/<id>/stream` and falls back to polling if SSE is unavailable. `POST /api/submissions/run` executes visible tests only. The evaluator uses the internal sandbox HTTP service when `SANDBOX_URL` is configured; production Compose requires the shared `SANDBOX_TOKEN`. Live API failures remain explicit loading/error/unauthorized states rather than falling back to fake data.

Each adapter method should normalize backend responses to the current frontend shape. The view layer should not know whether a result came from Supabase, Flask or a mock fixture.

## Run modes

```bash
# Frontend review without Supabase credentials
FRONTEND_ONLY=true PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000

# Normal backend mode after environment variables are configured
PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000
```

Normal mode requires `SECRET_KEY`, `SUPABASE_URL` and `SUPABASE_KEY`. Provider redirects may additionally use `FRONTEND_URL`, `OTP_REDIRECT_URL` and `GOOGLE_OAUTH_REDIRECT_URL`. For Redis-backed production submissions, set `REDIS_URL`, `SUBMISSION_QUEUE_MODE=redis`, `SANDBOX_URL`, `SANDBOX_TOKEN` and `SUBMISSION_WORKERS`. Production startup fails when required secrets are absent, and these values must be provided through environment configuration or a deployment secret store and never committed to the repository.

For the complete local container stack, copy `.env.example` to `.env`, apply migrations 001–004 plus the starter seed in Supabase, set a strong non-empty `SANDBOX_TOKEN`, then run `docker compose up --build`. For a credential-free Flask development run, set `LOCAL_DB=true`, `LOCAL_DB_PATH=instance/codehaven.sqlite3`, `FRONTEND_ONLY=false`, and start Flask directly; this uses real local SQLite persistence for accounts and learning records. Web and worker services use `app_network` for Supabase/external access and also join `sandbox_internal` to reach Redis and the sandbox. Redis and sandbox are not published to the host; only the web port is published. In the complete Compose stack, web requests enqueue submissions in Redis and the separate `backend.worker` process evaluates them. For a single-process local run without Redis, keep `SUBMISSION_QUEUE_MODE=thread`. Authenticated students can use `POST /api/submissions/run` for an immediate visible-test runtime result, or `POST /api/submissions` for a graded queued submission. The browser consumes `GET /api/submissions/<id>/stream` over SSE and falls back to `GET /api/submissions/<id>` polling if streaming is unavailable. Run `PYTHONPATH=. python3 scripts/validate_backend_env.py` to check Flask, Supabase schema and sandbox readiness. Docker validation requires Docker Engine; this repository’s CI validates Compose configuration without requiring live Supabase credentials.
