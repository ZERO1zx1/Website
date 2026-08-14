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
| Teacher | `backend/api/teacher.py` | `/api/teacher` | Teacher dashboard later |
| Analytics | `backend/api/analytics.py` | `/api/analytics` | Mastery, activity and skill map |

## Authentication schema prerequisite

Before enabling normal authentication, apply `backend/db/migrations/001_auth_roles.sql`. It adds `password_hash`, `requested_role` and `teacher_approval_status`, restricts role values to `owner`, `admin`, `teacher` and `student`, and adds an approval lookup index. Existing plaintext passwords must not be copied into `password_hash`; legacy accounts should complete a password reset before production login is enabled.

After the auth migration, apply `backend/db/migrations/002_learning_platform.sql`. It creates the idempotent learning-platform tables required by courses, modules, lessons, classes, enrollments, skills, problems, test cases, hints, submissions, evaluator results, teacher feedback, exams and mastery analytics. The migration also adds foreign keys, uniqueness constraints, query indexes and `updated_at` triggers. The application can run without sample content, but courses and problems must be seeded or created by a teacher before the authenticated learning screens contain live records.

Apply `backend/db/migrations/003_external_auth_identities.sql` to add the Supabase Auth identity link, provider name and avatar fields used by Gmail OTP and Google OAuth. In Supabase Auth, enable Email provider, configure the email template to include `{{ .Token }}` when a six-digit code is required, and add the configured `OTP_REDIRECT_URL` to the project redirect allow-list. Enable Google provider, set its Google client ID and client secret in Supabase Auth, and add `GOOGLE_OAUTH_REDIRECT_URL` to Supabase Auth URL Configuration. The Flask endpoints are `POST /api/auth/otp/request`, `POST /api/auth/otp/verify`, `GET /api/auth/google/start` and `GET /api/auth/google/callback`.

## Recommended integration order

Authentication is integrated first because all other screens need a current user and authorization state. Apply both schema migrations, verify password hashing and test owner/admin/teacher/student permissions, then use the login screen to establish the API session. The dashboard adapter now consumes normalized mastery and recent-submission data; the learning path and problem library adapters consume `/api/courses` and `/api/problems`. Submission integration remains the final student-flow step because it requires sandbox execution, asynchronous status handling and explicit loading/error states.

Each adapter method should normalize backend responses to the current frontend shape. The view layer should not know whether a result came from Supabase, Flask or a mock fixture.

## Run modes

```bash
# Frontend review without Supabase credentials
FRONTEND_ONLY=true PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000

# Normal backend mode after environment variables are configured
PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000
```

Normal mode requires `SECRET_KEY`, `SUPABASE_URL` and `SUPABASE_KEY`. Provider redirects may additionally use `FRONTEND_URL`, `OTP_REDIRECT_URL` and `GOOGLE_OAUTH_REDIRECT_URL`. These values must be provided through environment configuration and never committed to the repository.
