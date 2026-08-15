# Codehaven Training Assessments

Codehaven-ийн assessment module нь багш/админд сургалтын шалгалт үүсгэх, суралцагчид хугацаатай оролдлогоор шалгалт өгөх, хариултаа хадгалах, илгээсний дараа оноо болон progress report харах боломж олгодог.

## Student flow

Student нь authenticated dashboard-ийн **Assessments** хэсэгт орж нийтлэгдсэн шалгалтуудаа харна. `Begin exam` дарснаар server-side `exam_attempts` record үүсэж, timer эхэлнэ. Multiple-choice болон short-answer хариултууд autosave хийгдэж, `Save progress`-оор бүх хариултыг дахин хадгалж болно. Browser-ийн timer нь зөвхөн харагдац; submit хийх үед backend эхэлсэн хугацаа болон `duration_minutes`-ийг шалгадаг.

Шалгалт submit хийсний дараа server бүх асуултын answer key-тэй харьцуулж оноо бодно. Student-д hidden answer key зөвхөн graded result үед шаардлагатай хэсгээр ашиглагдаж, start/get exam response-д буцаагдахгүй. Оноо нь dashboard-ийн progress report, assessment card, exam summary-д хадгалагдана.

## Teacher/Admin flow

Teacher, admin, owner role бүхий хэрэглэгч Assessments view дээр **Build an exam** товчийг харна. Builder дээр title, description, duration, maximum attempts болон question-ууд нэмнэ. Question нь `multiple_choice`, `short_answer`, эсвэл `code` type-тэй байж болно. Эхний UI нь multiple-choice болон short-answer сургалтын checkpoint-д зориулагдсан бөгөөд answer key server талд хадгалагдана.

Teacher нь зөвхөн өөрийн үүсгэсэн exam-ийн aggregate report-ийг харна. Admin болон owner бүх assessment report-ийг хянаж болно. Student нь өөрийн attempt болон result-ийг л харна.

## API contract

| Endpoint | Purpose | Access |
|---|---|---|
| `GET /api/exams` | Published exam list and learner attempt summary | Student, teacher, admin, owner |
| `POST /api/exams` | Create an exam and its questions | Teacher, admin, owner |
| `GET /api/exams/<id>` | Exam detail; answer keys are staff-only | Authenticated roles |
| `POST /api/exams/<id>/attempts` | Start or resume a student attempt | Student |
| `GET /api/exams/attempts/<id>` | Read an owned or assigned attempt | Student or authorized staff |
| `PATCH /api/exams/attempts/<id>/answers/<question_id>` | Autosave one answer | Student owner |
| `POST /api/exams/attempts/<id>/submit` | Server-side grading and final result | Student owner |
| `GET /api/exams/<id>/report` | Aggregate score, pass rate, distribution | Teacher owner, admin, owner |
| `GET /api/analytics/progress-report` | Course, lesson, mastery, and exam report | Student own data; staff scoped data |

## Database setup

Local SQLite creates assessment tables automatically on startup. Production Supabase deployments must run `backend/db/migrations/005_assessments_and_progress.sql` after migrations `001` through `004`. The migration creates `exam_questions`, `exam_attempts`, and `exam_answers`, extends `exams`, adds indexes, and installs an update timestamp trigger.

The local development seed includes **Python foundations checkpoint** with three questions, a 20-minute duration, and three attempts. It is intended as useful training content for local verification, not as a fake dashboard statistic. User attempts and scores are persisted in `instance/codehaven.sqlite3`.

## Local verification

Start the backend with SQLite:

```bash
PYTHONPATH=. LOCAL_DB=true \
LOCAL_DB_PATH=/home/ubuntu/Website_latest/instance/codehaven.sqlite3 \
FLASK_ENV=development \
SECRET_KEY=local-development-secret-that-is-long-enough \
FRONTEND_ONLY=false \
python3 -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5059
```

Then open [http://127.0.0.1:5059/](http://127.0.0.1:5059/), register a student, open **Assessments**, begin the Python checkpoint, save answers, and submit. The progress report on Overview should show the latest exam attempt and best score.

Run the complete quality gate before committing:

```bash
bash ci/check.sh
pip-audit -r requirements.txt --progress-spinner off
```

The regression suite covers student answer ownership, answer-key redaction, attempt creation, autosave, grading, progress report hydration, and teacher builder permissions.
