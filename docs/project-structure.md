# Website project structure

## Зорилго

Codehaven нь Flask backend болон server-rendered HTML/CSS/JavaScript frontend-ийг нэг application дотор ажиллуулна. Feature бүр тодорхой ownership-тэй: page route нь HTML/Jinja-г, API blueprint нь JSON contract-ийг, service layer нь domain logic-ийг, DB wrapper нь persistence-ийг хариуцна.

## Canonical tree

```text
Website/
├── app.py                         # Flask app factory, page routes, health/readiness
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
│
├── backend/
│   ├── db.py                      # SQLite local / Supabase production gateway
│   ├── local_db.py                # SQLite schema, deterministic seed, cleanup
│   ├── rbac.py                    # Owner/Admin/Teacher/Student permissions
│   ├── api/
│   │   ├── auth.py                # Authentication and password recovery
│   │   ├── courses.py             # Courses, lessons, user-owned progress
│   │   ├── problems.py             # Coding problem data
│   │   ├── submissions.py          # Run, submit, status, feedback
│   │   ├── exams.py                # Exam Builder, attempts, autosave, grading
│   │   ├── analytics.py            # Dashboard and progress analytics
│   │   └── teacher.py              # Teacher/Admin operations
│   └── services/
│       ├── analytics.py            # Timestamp-based activity/streak metrics
│       ├── code_executor.py        # HTTP sandbox or Docker fallback
│       ├── submission_evaluator.py # Visible/hidden test grading
│       └── submission_queue.py     # Thread/Redis queue abstraction
│
├── frontend/
│   ├── templates/pages/
│   │   ├── base.html               # Public/auth shared layout
│   │   ├── home.html               # `/`, `/home`
│   │   ├── login.html              # `/login`
│   │   ├── register.html           # `/register`
│   │   ├── password_reset.html     # `/password-reset`
│   │   ├── workspace_base.html     # Authenticated shared shell
│   │   ├── workspace_dashboard.html# `/dashboard`
│   │   ├── learn.html              # `/learn`, `/courses`
│   │   ├── practice.html           # `/practice`
│   │   ├── assessments.html        # `/assessments`, `/exams`
│   │   ├── profile.html             # `/profile`
│   │   └── settings.html            # `/settings`
│   ├── static/css/
│   │   ├── style.css               # Workspace design system
│   │   ├── site/site.css            # Public/auth styling
│   │   └── workspace/               # Workspace extension directory
│   ├── static/js/
│   │   ├── app.js                  # Authenticated runtime
│   │   ├── adapters/api-adapter.js # API boundary
│   │   ├── pages/auth.js            # Auth page logic
│   │   ├── i18n/translations.js     # EN/MN dictionary
│   │   └── modules/monaco-editor.js # Editor integration
│   └── static/assets/
│       ├── images/
│       ├── icons/
│       └── fonts/
│
├── config/
│   └── roles.yml                   # Authoritative RBAC matrix
├── backend/db/migrations/          # Supabase migrations
├── backend/db/seed/                # Supabase production seed
├── sandbox/                        # Isolated code execution service
├── tests/                          # Regression and security tests
├── ci/                             # Canonical quality gate
└── docs/                           # Runbooks and integration guides
```

## Page and API boundary

| User experience | HTML route/template | Live API boundary |
|---|---|---|
| Public home | `/` → `pages/home.html` | None; marketing content only |
| Dashboard | `/dashboard` → `workspace_dashboard.html` | `/api/auth/me`, `/api/analytics/dashboard`, `/api/courses` |
| Learning | `/learn` → `learn.html` | `/api/courses`, lesson start/complete endpoints |
| Practice | `/practice` → `practice.html` | `/api/problems`, `/api/submissions`, sandbox health |
| Assessments | `/assessments` → `assessments.html` | `/api/exams`, attempts, answers, submit, report |
| Profile/preferences | `/profile`, `/settings` | `/api/auth/me` and account-owned settings |

The old all-in-one `frontend/templates/index.html` shell has been removed from the canonical structure. `/workspace` remains only as a compatibility alias to the canonical dashboard template; it does not render a second UI.

## Boundary rules

The browser does not trust a client-provided role. The API adapter sends the authenticated bearer token, and Flask enforces ownership and RBAC on every protected endpoint. A student can see only that student’s progress, answers, submissions, and attempts. Teacher/Admin/Owner permissions are checked server-side.

The frontend does not invent account statistics. Empty states such as “No study activity recorded yet” are rendered when the backend has no saved activity. The explicit frontend-only preview mode is an empty design-review state, not a demo learner or a production data source.

`backend/services/analytics.py` derives study minutes, daily activity, and streak from persisted lesson timestamps. Coding execution uses the HTTP sandbox when `SANDBOX_URL` is configured and falls back to Docker only when no HTTP sandbox is configured. Assessment submission grades on the server and redacts answer keys from student responses.

## Runtime sequence

```text
Browser page
    ↓
workspace_base.html + app.js
    ↓
static/js/adapters/api-adapter.js
    ↓
Flask API blueprint
    ↓
RBAC + ownership checks
    ↓
backend/services + backend/db.py
    ↓
SQLite in local development / Supabase in production
```

The canonical local quality gate is:

```bash
bash ci/check.sh
```

It compiles Python, runs regression tests, validates JavaScript syntax, checks the frontend structure, verifies the workflow and Compose contracts, and checks repository hygiene.
