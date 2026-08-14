# Website backend implementation report

**Repository:** `ZERO1zx1/Website`
**Branch:** `feat/frontend-redesign`
**Execution style:** AgentCore-style incremental checkpoints

## Хэрэгжсэн хүрээ

Backend-ийн folder structure, Python Flask API, Supabase gateway, Docker, YAML configuration, Markdown runbook, role/permission policy болон authentication security суурийг бэлдлээ. Frontend нь plain HTML, CSS, JavaScript хэвээр ажиллана. Frontend-only preview эвдрээгүй бөгөөд normal backend mode-д тусдаа API adapter автоматаар сонгогдоно.

## Backend architecture

| Хэсэг | Байрлал | Үүрэг |
|---|---|---|
| Application factory | `app.py` | Flask app, CORS, frontend shell, blueprint registration |
| API | `backend/api/` | Auth, courses, problems, submissions, teacher, analytics |
| Database | `backend/db.py` | Lazy Supabase client болон domain queries |
| RBAC | `backend/rbac.py` | YAML policy loader, role label, permission guard, bilingual errors |
| Configuration | `config/app.yml`, `config/roles.yml` | Runtime болон role policy-ийн source |
| Container | `Dockerfile`, `docker-compose.yml`, `.dockerignore` | Web API болон isolated sandbox orchestration |
| Migration | `backend/db/migrations/001_auth_roles.sql` | Password hash, owner role, teacher approval schema |
| Documentation | `docs/*.md` | Structure, integration, glossary, checkpoint болон runbook |

## Role and permission model

`owner` (**эзэмшигч**) нь website-ийн хамгийн өндөр эрхтэй role бөгөөд owner-level role assignment, бүх dashboard болон teacher panel-д хандах эрхтэй. `admin` (**администратор**) нь operational resource, user management болон teacher approval-г удирдана. `teacher` (**багш**) нь өөрийн class, course, problem болон teacher panel-ийг удирдана. `student` (**суралцагч**) нь өөрийн course, problem, submission болон progress-ийг ашиглана.

Public registration-ээр орсон бүх хэрэглэгчийн effective role нь `student`. Багш болох хүсэлт нь `requested_role = teacher`, `approval_status = pending` хэлбэрээр хадгалагдана. Owner эсвэл admin баталгаажуулсны дараа л effective role `teacher` болно. Client-ээс `role=owner` гэх мэтээр илгээсэн утгыг backend хүлээж авахгүй.

## Security improvements

Authentication нь plaintext password comparison-оос password hash verification руу шилжсэн. Production mode-д `SECRET_KEY` байхгүй бол app fail-fast хийнэ. Supabase client нь lazy initialization-тэй болсон тул frontend-only test болон credentialгүй module import боломжтой. CORS wildcard ашиглахаа больж `CORS_ORIGINS` environment variable-аар explicit origin авна. JWT-ийн хугацаа 24 цаг байна.

API error нь тогтвортой code, English message болон Mongolian message-тэй байна. Жишээ нь `permission_denied` кодын Монгол мессеж нь “Танд энэ үйлдлийг хийх зөвшөөрөл байхгүй байна.” гэж байна.

## API нэмэлтүүд

| Endpoint | Эрх |
|---|---|
| `GET /api/analytics/dashboard` | Өөрийн student dashboard; owner/admin мөн permission-оор хандаж болно |
| `GET /api/teacher/dashboard` | Owner, admin, teacher |
| `GET /api/teacher/classes/<class_id>/analytics` | Owner/admin бүх class; teacher зөвхөн өөрийн class |
| `GET /api/auth/pending-teachers` | Owner/admin |
| `POST /api/auth/approve-teacher/<user_id>` | Owner/admin |
| `POST /api/auth/reject-teacher/<user_id>` | Owner/admin |
| `PATCH /api/auth/users/<user_id>/role` | Зөвхөн owner |

## Validation evidence

| Шалгалт | Үр дүн |
|---|---:|
| App configuration tests | Passed |
| Auth security tests | Passed |
| RBAC tests | Passed |
| Frontend shell tests | Passed |
| Executor tests | Passed |
| Нийт regression test | **15 passed** |
| Python compile | Passed |
| JavaScript syntax | Passed |
| YAML parse: roles, app, compose | Passed |
| Normal backend route registration | Passed |
| Docker Compose runtime validation | Skipped; sandbox-д Docker CLI байхгүй |

Тестийн үлдсэн warning нь `backend/services/code_executor.py` доторх existing `datetime.utcnow()` deprecation warning бөгөөд test failure биш. Үүнийг дараагийн жижиг technical-debt task-аар timezone-aware datetime болгон шинэчилж болно.

## Дараагийн хэрэгжүүлэх дараалал

Database migration-г Supabase дээр ажиллуулсны дараа бодит auth login/register-ийг frontend API adapter-тэй холбоно. Дараа нь current user, student dashboard, learning path, practice problems, teacher panel болон submissions-ийг нэг нэгээр нь холбоно. Endpoint бүр дээр loading, empty, error, unauthorized болон Mongolian/English response state-ийг тусад нь баталгаажуулна.

Дараагийн integration эхлэхээс өмнө `.env.example`-ийг хуулж `.env` үүсгэнэ. Production secret, Supabase key болон populated `.env` файлыг repository-д commit хийхгүй.
