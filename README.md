# CodeCraft Academy

CodeCraft Academy нь Монгол хэл дээрх Flask + Jinja олон хуудаст сургалтын платформ. Энэ repository нь бүтээгдэхүүний canonical эх сурвалж бөгөөд тусдаа FastAPI/SPA backend агуулаагүй.

## Гол боломж

- Domain-based frontend: `layouts`, `pages`, `account`, `learning`, `admin`, `components` template folder-ууд
- Нүүр, хөтөлбөр, курс, хичээл, workspace, dashboard, auth, profile гэсэн responsive Jinja хуудсууд
- `Practice Grounds`, `Bug Lab`, `Guided Project`, `Portfolio Project` бүхий learning path; Python, HTML, CSS, JavaScript-ийн 15 challenge
- Admin Content Studio-оор lesson/challenge, starter code, automated test, hidden test, hint, XP болон draft metadata үүсгэнэ
- Python/JavaScript sandbox grading, HTML/CSS static requirement grading, submission queue ба accepted result feedback
- Server-side XP event ledger, current/longest streak, badge evaluator болон dashboard summary
- Supabase PostgreSQL дээрх profile, хичээл ба курсийн ахиц, quiz attempt persistence; authentication нь CodeCraft app-owned
- Student/teacher/admin/owner RBAC болон суралцагчийн өгөгдлийг тусгаарласан RLS
- Redis queue болон тусгаарласан Docker sandbox; байхгүй үед execute API аюулгүйгаар `503` буцаана
- Pytest, Ruff, Bandit, pip-audit, Docker build бүхий CI

## Local ажиллуулах

Python 3.12, Git шаардлагатай.

```bash
git clone https://github.com/ZERO1zx1/Website.git
cd Website
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python run.py
# эсвэл compatibility хэлбэрээр:
python -m flask --app app:create_app run
```

Credential бэлэн биш бол `.env`-д `FRONTEND_ONLY=true` тавьж UI-г sandbox, Redis, Supabase-гүй ажиллуулж болно.

## Environment variable

- `SECRET_KEY`: production-д заавал урт, санамсаргүй утга; CodeCraft app JWT/session signing-д ашиглана
- `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`: Supabase database connection болон public configuration
- `SUPABASE_SERVICE_ROLE_KEY`: зөвхөн Flask server-ийн database key; browser болон build argument-д хийж болохгүй
- `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`: CodeCraft-ийн шууд Google OAuth; Supabase Auth provider биш
- `GOOGLE_OAUTH_REDIRECT_URL`: Google Cloud Console-д бүртгүүлэх callback URL
- `CORS_ORIGINS`: comma-аар тусгаарласан яг зөвшөөрөх origin
- `SANDBOX_URL`, `SANDBOX_TOKEN`: internal code runner
- `SUBMISSION_QUEUE_MODE=redis`, `REDIS_URL`: distributed queue сонголт

Бүрэн жагсаалтыг [.env.example](.env.example)-ээс харна уу. Browser public config-оо зөвхөн `/api/public-config` endpoint-оос авна.

## Supabase

Шинэ project дээр `backend/db/migrations` файлуудыг дараах дарааллаар ажиллуулна: `001_auth_roles.sql`, `002_learning_platform.sql`, `003_external_auth_identities.sql`, `004_content_studio.sql`, `005_gamification.sql`, `006_local_app_auth.sql`. `006_local_app_auth.sql` нь CodeCraft-ийн `app_auth_identities` хүснэгт үүсгэж, password hash болон local app UUID-г learning persistence-тэй холбодог. Supabase Auth хэрэглэгч үүсгэхгүй.

`005_gamification.sql` нь XP ledger, learning day, streak profile, badge definition болон user badge хүснэгтүүдийг үүсгэнэ. `006_local_app_auth.sql` apply хийгдээгүй үед local Login/Register database auth ажиллахгүй.

Google ашиглах бол Google Cloud Console-д `/api/auth/google/callback` callback-ийг бүртгэж `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` тохируулна. Google OAuth flow нь Supabase Auth provider ашиглахгүй.

## Content Studio

Админ UI нь `/admin` дээр байрлана. Backend mode-д `admin` эсвэл `owner` эрхтэй session шаардлагатай. Шинэ content-ийн дараалал нь Basic info → explanation/starter code → automated tests → hints → draft хадгалах → test хийж publish хийх байна. API contract нь `POST /api/admin/content`; test болон hint-үүдийг нэг payload дотор үүсгэнэ.

Frontend template-ийн domain бүтэц болон backend-ийн mapping-ийг [docs/architecture.md](docs/architecture.md)-д баримтжуулна.

## Sandbox ба queue

Default local тохиргоонд host process дээр хэрэглэгчийн код ажиллахгүй. Бүрэн stack:

```bash
docker compose up --build
```

Sandbox нь non-root user, read-only root filesystem, network isolation, capability drop, PID/CPU/memory/time/file-size хязгаар ашиглана. Production-д `SANDBOX_TOKEN`-ийг заавал сольж, service-ийг public internet-д бүү гарга.

## Шалгалт

```bash
python -m pytest -q
python -m ruff check .
python -m bandit -q -r app.py backend sandbox
python -m pip_audit -r requirements.txt
docker build -t codecraft-academy .
```

## Deployment

Production-д `FLASK_ENV=production`, HTTPS, managed secrets, migration backup, Redis queue, sandbox private network ашиглана. `/api/health` нь process health, `/api/ready` нь config болон Supabase connectivity-г шалгана.

## Troubleshooting

- `/api/ready` 503: response дахь `missing` эсвэл `dependency`-г шалга.
- Execute 503: sandbox URL/token тохируулаагүй; host execution руу fallback хийхгүй.
- Google login буцахгүй: Supabase redirect URL болон `GOOGLE_OAUTH_REDIRECT_URL` ижил эсэхийг шалга.
- Progress хадгалагдахгүй: `006_local_app_auth.sql` migration ажилласан, хэрэглэгчийн CodeCraft app identity болон database connection-ийг шалга.

Нэгтгэлийн mapping: [docs/repository-consolidation-audit.md](docs/repository-consolidation-audit.md).

Production migration, secret, sandbox, queue, rollback checklist: [docs/production-runbook-mn.md](docs/production-runbook-mn.md).
