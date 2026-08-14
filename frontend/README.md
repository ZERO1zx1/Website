# Flask-served frontend

The frontend is a server-rendered HTML shell with modular CSS and browser JavaScript. Flask serves `templates/index.html` and the assets under `static/`; the browser does not require a separate Node build step.

## Folder structure

```text
frontend/
├── templates/index.html
└── static/
    ├── css/style.css
    └── js/
        ├── app.js
        ├── data/curriculum.js
        ├── i18n/translations.js
        ├── monaco-editor.js
        └── adapters/api-adapter.js
```

## Runtime modes

`FRONTEND_ONLY=true` enables an explicitly labelled preview mode. It uses the local fixture boundary in `app.js` for design review and does not require Supabase credentials. This mode is not a production data source.

`FRONTEND_ONLY=false` is the normal backend mode. In development, when Supabase credentials are absent, Flask uses the file-backed SQLite database configured by `LOCAL_DB_PATH`; this is real persistence for accounts, courses, problems, lesson progress, dashboard metrics, and submissions, not a browser fixture. After authentication, `api-adapter.js` calls the live Flask routes for current user, dashboard, courses, lessons, lesson completion, problems, visible-test execution, graded submissions, and submission status. The adapter normalizes response shapes, sends the bearer token in the request header, applies a timeout, clears expired sessions, and does not replace failed requests with mock data.

## Submission flow

The editor sends `POST /api/submissions/run` for visible-test execution and `POST /api/submissions` for graded evaluation. Graded submissions are tracked through `GET /api/submissions/<id>/stream` with a polling fallback. Run and Submit controls are disabled while a request is active to prevent duplicate requests. Hidden test inputs, expected outputs, and solutions are not rendered to students. Completing a lesson sends `POST /api/courses/lessons/<lesson_id>/complete` and refreshes the dashboard from persisted backend data.

## Local checks

From the repository root, run:

```bash
node --check frontend/static/js/app.js
node --check frontend/static/js/adapters/api-adapter.js
node --check frontend/static/js/monaco-editor.js
```

The canonical backend integration runbook is [`../docs/backend-integration.md`](../docs/backend-integration.md). The visible authenticated experience does not offer demo-learner continuation; preview mode remains only as an explicit developer setting for design review. Authenticated backend mode is the source of truth for user data.
