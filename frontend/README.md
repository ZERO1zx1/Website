# Flask-served frontend

Codehaven нь Flask-ийн server-rendered HTML frontend бөгөөд тусдаа page templates, shared CSS, page JavaScript, workspace modules, болон static assets-ийг ойлгомжтой дэд бүтэцтэйгээр зохион байгуулдаг. Тусдаа Node build step шаардлагагүй.

## Folder structure

```text
frontend/
├── templates/
│   ├── index.html                  # Бүрэн authenticated learning workspace
│   └── pages/
│       ├── base.html               # Shared header, navigation, footer, assets
│       ├── home.html               # Public landing page
│       ├── login.html              # Sign in page
│       ├── register.html           # Account creation page
│       ├── password_reset.html     # Password recovery request/confirm page
│       └── dashboard.html          # Live authenticated dashboard page
└── static/
    ├── css/
    │   ├── style.css               # Existing workspace design system
    │   ├── site/site.css            # Shared multi-page site styling
    │   └── workspace/               # Future workspace-specific style layers
    ├── js/
    │   ├── app.js                  # Full learning workspace runtime
    │   ├── pages/auth.js            # Login, register, reset, OAuth, dashboard page logic
    │   ├── modules/monaco-editor.js # Editor module
    │   ├── data/curriculum.js      # Curriculum content boundary
    │   ├── i18n/translations.js    # EN/MN translations for workspace
    │   └── adapters/api-adapter.js # Live Flask API adapter
    └── assets/
        ├── images/                 # Page images and logos
        ├── icons/                  # SVG and icon assets
        ├── fonts/                  # Project-owned fonts, if added
        └── README.md
```

## Page routes

| Page | Flask route | Purpose |
|---|---|---|
| Home | `/home` | Public learning platform landing page |
| Login | `/login` | Email/password, Google provider, and email-code entry point |
| Register | `/register` | Real student account registration |
| Password reset | `/password-reset` | Local reset token flow and Supabase recovery entry point |
| Dashboard | `/dashboard` | Authenticated live metrics and next lessons |
| Workspace | `/` | Full learning path, practice, assessments, profile, and preferences |

## Runtime modes

`FRONTEND_ONLY=true` enables an explicitly labelled preview mode. It uses the local fixture boundary in `app.js` for design review and does not require Supabase credentials. This mode is not a production data source.

`FRONTEND_ONLY=false` is the normal backend mode. In development, when Supabase credentials are absent, Flask uses the file-backed SQLite database configured by `LOCAL_DB_PATH`; this is real persistence for accounts, courses, problems, lesson progress, dashboard metrics, and submissions, not a browser fixture. After authentication, the API adapter calls the live Flask routes for current user, dashboard, courses, lessons, lesson completion, problems, visible-test execution, graded submissions, and submission status.

## Local checks

From the repository root, run:

```bash
python3 -m compileall -q .
PYTHONPATH=. pytest -q
node --check frontend/static/js/app.js
node --check frontend/static/js/pages/auth.js
node --check frontend/static/js/adapters/api-adapter.js
node --check frontend/static/js/modules/monaco-editor.js
```

The canonical backend integration runbook is [`../docs/backend-integration.md`](../docs/backend-integration.md). The visible authenticated experience does not offer demo-learner continuation; backend mode is the source of truth for user data.
