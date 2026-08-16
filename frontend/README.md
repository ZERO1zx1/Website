# Flask-served frontend

Codehaven нь Flask-ийн server-rendered HTML frontend бөгөөд public page, authenticated workspace page, shared layout, CSS, page JavaScript, API adapter, болон static assets-ийг тусдаа boundary-тайгаар зохион байгуулдаг. Node build step шаарддаггүй.

## Folder structure

```text
frontend/
├── templates/
│   └── pages/
│       ├── base.html                  # Public/auth shared layout
│       ├── home.html                  # Public landing page
│       ├── login.html                 # Sign in page
│       ├── register.html              # Account creation page
│       ├── password_reset.html        # Password recovery page
│       ├── workspace_base.html        # Authenticated shared layout
│       ├── workspace_dashboard.html   # Live dashboard
│       ├── learn.html                 # Course and lesson flow
│       ├── practice.html              # Coding practice library
│       ├── assessments.html           # Exam Builder and Student Exam View
│       ├── profile.html               # Account/profile page
│       └── settings.html              # Language/theme/editor preferences
└── static/
    ├── css/
    │   ├── style.css                  # Authenticated workspace design system
    │   ├── site/site.css              # Public/auth site styling
    │   └── workspace/                 # Workspace style extension directory
    ├── js/
    │   ├── app.js                     # Authenticated workspace runtime
    │   ├── pages/auth.js               # Login, register, reset, OAuth logic
    │   ├── modules/monaco-editor.js    # Editor module
    │   ├── data/curriculum.js          # Non-user curriculum metadata
    │   ├── i18n/translations.js        # EN/MN translations
    │   └── adapters/api-adapter.js     # Live Flask API adapter
    └── assets/
        ├── images/
        ├── icons/
        ├── fonts/
        └── README.md
```

## Page routes

| Page | Flask route | Purpose |
|---|---|---|
| Public home | `/`, `/home` | Public learning platform landing page |
| Login | `/login` | Email/password, Google provider, and email-code entry point |
| Register | `/register` | Real student account registration |
| Password reset | `/password-reset` | Local reset token flow and Supabase recovery entry point |
| Dashboard | `/dashboard` | Authenticated live metrics and next lessons |
| Learning | `/learn`, `/courses` | Courses, modules, lesson preview, and user-owned status |
| Practice | `/practice` | Problems, live sandbox execution, and persisted submissions |
| Assessments | `/assessments`, `/exams` | Exam list, Exam Builder, attempts, grading, and teacher reports |
| Profile | `/profile` | Authenticated account and role information |
| Preferences | `/settings` | Language, theme, and editor preferences |
| Workspace alias | `/workspace` | Compatibility alias that renders the canonical dashboard page |

The old all-in-one `index.html` shell is no longer used or served. Each major experience now has its own Jinja template while all authenticated pages share `workspace_base.html`.

## Runtime modes

`FRONTEND_ONLY=true` enables an explicitly labelled preview mode for layout review. It does not create a preset learner and does not display fake account statistics. Production-like user behavior requires backend mode.

`FRONTEND_ONLY=false` is the normal backend mode. In development, when Supabase credentials are absent, Flask uses the file-backed SQLite database configured by `LOCAL_DB_PATH`; this is real persistence for accounts, courses, problems, lesson progress, dashboard metrics, assessments, and submissions. After authentication, the API adapter calls live Flask routes for current user, dashboard, courses, lessons, lesson completion, problems, sandbox execution, graded submissions, exam attempts, and analytics.

## Local checks

From the repository root, run:

```bash
python3 -m compileall -q .
PYTHONPATH=. pytest -q
node --check frontend/static/js/app.js
node --check frontend/static/js/pages/auth.js
node --check frontend/static/js/adapters/api-adapter.js
node --check frontend/static/js/modules/monaco-editor.js
bash ci/check.sh
```

The canonical backend integration runbook is [`../docs/backend-integration.md`](../docs/backend-integration.md). The visible authenticated experience does not offer demo-learner continuation; backend mode is the source of truth for user data.
