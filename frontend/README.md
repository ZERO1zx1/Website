# Codehaven Demo V1 Frontend

This directory contains the complete frontend-only Demo V1 website for the Codehaven programming education platform. It uses plain HTML, CSS, and JavaScript. The current implementation is intentionally backed by local mock data; Flask, Supabase, authentication providers, roles, and live persistence remain a later integration phase.

## Folder structure

```text
frontend/
├── templates/
│   └── index.html                 # Complete HTML shell and all application screens
└── static/
    ├── css/
    │   └── style.css              # Design tokens, components, themes, responsive rules
    └── js/
        ├── app.js                 # Shared state, navigation, renderers, interactions
        ├── data/
        │   └── curriculum.js      # Courses, modules, practice, tags, keywords
        ├── i18n/
        │   └── translations.js    # EN/MN dictionaries and plain text mappings
        ├── monaco-editor.js        # Editor integration boundary
        └── adapters/
            ├── api-adapter.js     # Backend-ready adapter contract and live API mode
            └── README.md          # Adapter integration notes
```

## Included frontend experience

The website includes a public landing page, sign-in/register preview, Python, HTML, CSS, JavaScript, Flask, and Full-stack learning paths, course cards, tags, keyword search, selected modules, lesson preview, lesson completion in demo mode, practice problems, code editor mock flow, assessments, profile, preferences, EN/MN localization, dark/light theme, responsive mobile layout, focus-visible keyboard states, and live-region feedback. The shared app shell stays in `app.js`, while curriculum content and translations are isolated in their own modules so future backend replacement does not require rewriting the UI.

## Local serving

The recommended local command from the repository root is:

```bash
FRONTEND_ONLY=true PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000
```

Then open `http://localhost:5000`. The Flask shell serves `templates/index.html` and the static CSS/JavaScript assets. No frontend build step or framework is required.

## Demo versus backend

Demo V1 stores the selected language, theme, and demo session in browser storage and uses local mock data. The `api-adapter.js` file preserves the contract for the later Flask/Supabase phase. Do not treat demo completion, demo profile values, or mock progress as persisted production records.
