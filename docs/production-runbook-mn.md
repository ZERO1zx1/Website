# CodeCraft Academy production runbook

Энэ runbook нь CodeCraft Academy-г development preview-оос Supabase болон private sandbox ашигласан production орчинд гаргах дарааллыг тодорхойлно. **Local smoke test амжилттай болсон нь real Supabase migration, OAuth, queue эсвэл sandbox production-д бэлэн болсон гэсэн үг биш.**

## 1. Нууц тохиргоо

Production secret manager-д дараах утгуудыг тусад нь хадгална. `.env` файлыг repository-д commit хийхгүй.

| Тохиргоо | Зорилго | Production шаардлага |
|---|---|---|
| `SECRET_KEY` | App JWT ба session cookie | Урт, санамсаргүй, зөвхөн server-side |
| `SUPABASE_URL` | Supabase project endpoint | Бодит project URL |
| `SUPABASE_PUBLISHABLE_KEY` | Public Auth/browser bridge | Publishable key; service role биш |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-side privileged DB/Auth operation | Browser, logs, build artifact-д огт гаргахгүй |
| `CORS_ORIGINS` | Зөвшөөрөх frontend origins | Wildcard (`*`) хэрэглэхгүй |
| `SANDBOX_URL` | Private code runner | Public internet-ээс шууд нээхгүй |
| `SANDBOX_TOKEN` | Runner service authentication | Placeholder биш, rotation-той secret |
| `SANDBOX_REQUIRED=true` | Host process code execution-ийг хориглох | Production-д заавал true |
| `SUBMISSION_QUEUE_MODE=redis` | Distributed worker queue | Production-д Redis ашиглана |
| `REDIS_URL` | Submission queue backend | TLS/private network тохируулна |

## 2. Supabase migration дараалал

Migration-уудыг шинэ project дээр дараах нэрийн дарааллаар apply хийнэ.

```text
backend/db/migrations/001_auth_roles.sql
backend/db/migrations/002_learning_platform.sql
backend/db/migrations/003_external_auth_identities.sql
backend/db/migrations/004_content_studio.sql
backend/db/migrations/005_gamification.sql
```

Migration хийхээс өмнө schema backup/export үүсгэнэ. Apply хийсний дараа дараах хүснэгтүүд болон RLS policy-ийг Supabase SQL editor-оос шалгана.

| Бүлэг | Гол хүснэгт/объект | Шалгах зүйл |
|---|---|---|
| Auth projection | `profiles`, role policy | Auth UUID болон role зөв холбогдсон эсэх |
| Learning | `course_progress`, `lesson_progress`, `quiz_attempts` | Нэг хэрэглэгч зөвхөн өөрийн мөрөө унших/өөрчлөх эсэх |
| Content Studio | `content_versions`, problem metadata | Teacher/admin gate болон draft/published status |
| Gamification | `gamification_profiles`, `xp_events`, `learning_streaks`, `badges`, `user_badges` | Unique key, idempotency constraint, user ownership |

Энэ repository-ийн одоогийн `gamification.py` Python түвшинд XP, streak, badge логик хэрэгжүүлдэг. Concurrent worker үед cross-table атомик байдлыг баталгаажуулахын тулд дараагийн hardening алхамд XP ledger, profile aggregate, streak update, badge insert-ийг нэг Supabase RPC/transaction function болгон шилжүүлнэ.

## 3. Deploy дараалал

```bash
cp .env.example .env
# secret manager-ийн production утгуудыг тохируулна
python -m pytest -q
python -m ruff check .
python -m bandit -q -r app.py backend sandbox
python -m pip_audit -r requirements.txt
python run.py
```

Production process нь `FLASK_ENV=production` үед `SECRET_KEY`-гүй эхлэх ёсгүй. Deploy хийсний дараа `/api/health` process амьд эсэх, `/api/ready` шаардлагатай configuration болон Supabase connectivity бэлэн эсэхийг шалгана.

## 4. Sandbox ба submission worker

Sandbox service-ийг app server-ээс тусдаа private network-д ажиллуулна. Runner нь non-root user, read-only filesystem, network isolation, capability drop, CPU/memory/time/PID/file-size limit-тай хэвээр байна. `SANDBOX_TOKEN`-ийг app болон sandbox дээр ижил боловч secret manager-ээс injection хийнэ.

Production smoke sequence нь нэг зөв Python challenge, нэг буруу Python challenge, нэг зөв HTML/CSS static challenge, нэг timeout/resource-limit challenge-ийг тус тус илгээнэ. Accepted result нь submission result, mastery, XP event, streak activity-д хүрсэн эсэхийг шалгана. Pending job удаан байвал Redis queue болон worker log-ийг шалгаж, хэрэглэгчийн code-г host process дээр ажиллуулах fallback хийхгүй.

## 5. Content publishing policy

Static `course_data.py` болон `learning_experiences.py` нь одоогийн built-in catalog-ийн fallback source хэвээр. Admin Content Studio-оор үүсгэсэн **published** DB content нь тухайн slug/type дээр learner API-д түрүүлж харагдах ёстой; DB content байхгүй үед static catalog харагдана. Draft болон archived content суралцагчийн catalog-д орохгүй.

Publish хийхийн өмнө title, slug, language, starter code, visible tests, hidden tests, hints, XP reward, expected runtime-ийг шалгана. Publish хийсний дараа `/practice`, `/workspace`, lesson detail болон submission API дээр тухайн content нэг ижил slug-аар resolve болж байгаа эсэхийг шалгана.

## 6. Rollback ба incident response

Migration алдаа гарвал дараагийн migration-ийг зогсоож, backup болон Supabase migration log-ийг хадгална. Code deploy rollback хийхдээ өмнөх application image/commit рүү буцаах боловч аль хэдийн apply болсон additive migration-ийг дур мэдэн устгахгүй. Sandbox compromise сэжиглэвэл sandbox token rotation, worker pause, private network isolation, submission audit log preservation дарааллаар ажиллана.

## 7. Одоогийн орчны хязгаарлалт

Энэ development орчинд `SUPABASE_URL`, secret key, sandbox URL/token бодит production утгаар тохируулагдаагүй бөгөөд Docker суулгагдаагүй байж болно. Иймээс энд баталгаажсан зүйл нь template render, JavaScript syntax, unit/regression test, local route smoke юм. **Real Supabase migration apply, OAuth login, Redis worker, Docker sandbox build, production readiness-г тусад нь operator credentials болон deployment environment дээр баталгаажуулна.**
