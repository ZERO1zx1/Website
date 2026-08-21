# CodeCraft Academy

CodeCraft Academy нь Монгол хэл дээрх Flask + Jinja олон хуудаст сургалтын платформ. Энэ repository нь бүтээгдэхүүний canonical эх сурвалж бөгөөд тусдаа FastAPI/SPA backend агуулаагүй.

## Гол боломж

- Нүүр, хөтөлбөр, курс, хичээл, workspace, dashboard, auth, profile гэсэн responsive Jinja хуудсууд
- Supabase PostgreSQL/Auth/Realtime дээрх UUID profile, хичээл ба курсийн ахиц, quiz attempt
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
python -m flask --app app:create_app run
```

Credential бэлэн биш бол `.env`-д `FRONTEND_ONLY=true` тавьж UI-г sandbox, Redis, Supabase-гүй ажиллуулж болно.

## Environment variable

- `SECRET_KEY`: production-д заавал урт, санамсаргүй утга
- `SUPABASE_URL`, `SUPABASE_PUBLISHABLE_KEY`: public Supabase тохиргоо
- `SUPABASE_SERVICE_ROLE_KEY`: зөвхөн Flask server secret; browser болон build argument-д хийж болохгүй
- `CORS_ORIGINS`: comma-аар тусгаарласан яг зөвшөөрөх origin
- `SANDBOX_URL`, `SANDBOX_TOKEN`: internal code runner
- `SUBMISSION_QUEUE_MODE=redis`, `REDIS_URL`: distributed queue сонголт

Бүрэн жагсаалтыг [.env.example](.env.example)-ээс харна уу. Browser public config-оо зөвхөн `/api/public-config` endpoint-оос авна.

## Supabase

Шинэ project дээр `supabase/migrations`-ийн файлуудыг нэрийн дарааллаар ажиллуулна. Google redirect URL нь `/api/auth/google/callback`. Дэлгэрэнгүй: [docs/supabase-setup.md](docs/supabase-setup.md).

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
- Progress хадгалагдахгүй: migration ажилласан, хэрэглэгч Supabase Auth identity-тай эсэхийг шалга.

Нэгтгэлийн mapping: [docs/repository-consolidation-audit.md](docs/repository-consolidation-audit.md).
