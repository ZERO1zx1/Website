# Backend integration plan

## Current boundary

The frontend is a plain HTML, CSS and JavaScript application rendered by Flask. It currently uses `mockAdapter` and does not make direct API requests. The backend is now organized under `backend/` and remains available in normal Flask mode.

## API groups

| Group | Blueprint location | Prefix | Frontend consumer |
|---|---|---|---|
| Authentication | `backend/api/auth.py` | `/api/auth` | Login, register, current user, role |
| Courses | `backend/api/courses.py` | `/api/courses` | Learning path and modules |
| Problems | `backend/api/problems.py` | `/api/problems` | Practice library and filters |
| Submissions | `backend/api/submissions.py` | `/api/submissions` | Run/submit code and result status |
| Teacher | `backend/api/teacher.py` | `/api/teacher` | Teacher dashboard later |
| Analytics | `backend/api/analytics.py` | `/api/analytics` | Mastery, activity and skill map |

## Recommended integration order

Authentication should be integrated first because all other screens need a current user and authorization state. The next step is to replace dashboard mock data with normalized analytics and submission summaries. Learning path and problem library follow. Submission integration comes last among the student flows because it requires sandbox execution, asynchronous status handling and explicit loading/error states.

Each adapter method should normalize backend responses to the current frontend shape. The view layer should not know whether a result came from Supabase, Flask or a mock fixture.

## Run modes

```bash
# Frontend review without Supabase credentials
FRONTEND_ONLY=true PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000

# Normal backend mode after environment variables are configured
PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000
```

Normal mode requires `SECRET_KEY`, `SUPABASE_URL` and `SUPABASE_KEY`. These values must be provided through environment configuration and never committed to the repository.
