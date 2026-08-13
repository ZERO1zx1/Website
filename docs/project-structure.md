# Website project structure

## Зорилго

Repository нь frontend болон backend-ийг нэг application дотор ажиллуулж болох боловч тусдаа ownership, dependency болон integration boundary-тай байхаар зохион байгуулагдана. Frontend нь plain HTML, CSS, JavaScript хэвээр үлдэнэ. Backend нь Flask API, Supabase client, route blueprint болон service layer-ээ `backend/` дотор төвлөрүүлнэ.

## Target tree

```text
Website/
├── app.py                         # Flask application factory and shell route
├── requirements.txt
├── .env.example
├── README.md
├── backend/
│   ├── __init__.py
│   ├── db.py                      # Supabase database gateway
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── courses.py
│   │   ├── problems.py
│   │   ├── submissions.py
│   │   ├── teacher.py
│   │   └── analytics.py
│   └── services/
│       ├── __init__.py
│       ├── code_executor.py
│       └── submission_evaluator.py
├── frontend/
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       ├── js/
│       │   ├── app.js
│       │   ├── monaco-editor.js
│       │   └── adapters/
│       │       └── README.md
│       └── assets/
├── sandbox/
│   ├── Dockerfile
│   └── runner.py
├── tests/
│   ├── test_frontend_shell.py
│   └── test_code_executor.py
└── docs/
    ├── project-structure.md
    ├── frontend-design-handoff.md
    ├── frontend-uiux-final-report-mn.md
    └── backend-integration.md
```

## Boundary rules

`frontend/` нь presentation болон browser interaction-ийг хариуцна. Browser code нь backend route руу шууд scattered `fetch` хийхгүй; `mockAdapter` эсвэл дараагийн `apiAdapter` interface-ээр дамжина. `backend/api/` нь request validation, authentication болон response contract-ийг хариуцна. `backend/services/` нь code execution, evaluation болон domain workflow-ийг хариуцна. `backend/db.py` нь Supabase client-ийн ганц gateway байна.

`FRONTEND_ONLY=true` үед backend blueprint болон Supabase import-ууд ачаалагдахгүй. Ингэснээр frontend designer болон developer нь credential шаардахгүйгээр UI-г ажиллуулж чадна. Normal mode үед `app.py` backend API blueprint-үүдийг `/api/*` prefix-ээр бүртгэнэ.

## Migration map

| Одоогийн байрлал | Шинэ байрлал | Тайлбар |
|---|---|---|
| `db.py` | `backend/db.py` | Database gateway-ийг backend namespace-д оруулна |
| `routes/*.py` | `backend/api/*.py` | API blueprint-үүдийг route-оос api гэж тодорхой болгоно |
| `services/*.py` | `backend/services/*.py` | Domain/service layer-ийг backend namespace-д оруулна |
| `frontend/templates/*` | Хэвээр | Browser presentation layer |
| `frontend/static/css/*` | Хэвээр | Theme болон component system |
| `frontend/static/js/app.js` | Хэвээр | UI state; adapter boundary хадгална |
| `sandbox/*` | Хэвээр | Docker runtime context тусдаа байна |

## Backend integration sequence

Эхний integration нь authentication adapter-ээс эхэлнэ. Дараа нь current user, learning path, problems, submissions гэсэн дарааллаар бодит endpoint-үүдийг mock method-оор солино. Нэг endpoint холбосны дараа response shape, loading state, empty state, error state болон unauthorized state-ийг тусад нь шалгана. Бүх backend холболт бэлэн болсны дараа `FRONTEND_ONLY` preview-г устгахгүй; энэ нь UI regression болон design review-д хэрэгтэй хэвээр байна.
