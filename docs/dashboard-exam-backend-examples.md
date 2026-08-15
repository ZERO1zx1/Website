# Dashboard Analytics, Supabase Roles, and Exam Backend Examples

This guide matches the current Codehaven contracts. The current role matrix is defined in `config/roles.yml`; the assessment routes are in `backend/api/exams.py`; the production assessment schema is `backend/db/migrations/005_assessments_and_progress.sql`.

## 1. Chart.js dashboard learning analytics

Include Chart.js in the workspace template. In production, pin the version or serve it from the project's approved asset pipeline rather than trusting an unpinned third-party script.

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<canvas id="learning-analytics-chart" aria-label="Learning activity over time"></canvas>
<canvas id="course-progress-chart" aria-label="Course progress"></canvas>
```

Load the authenticated dashboard response and render backend-owned values. This example expects the current endpoint `GET /api/analytics/dashboard`.

```javascript
const token = sessionStorage.getItem('codehaven-access-token');

async function getDashboardAnalytics() {
  const response = await fetch('/api/analytics/dashboard', {
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });

  if (!response.ok) {
    throw new Error('Dashboard analytics could not be loaded.');
  }
  return response.json();
}

let learningChart;
let courseChart;

async function renderLearningAnalytics() {
  const dashboard = await getDashboardAnalytics();
  const report = dashboard.progress_report || {};
  const courses = report.courses || [];

  // The current backend returns aggregate study_minutes. If a future API adds
  // daily_activity, use it here; do not invent daily values in the frontend.
  const activity = dashboard.daily_activity || [];
  const labels = activity.map((item) => item.date);
  const minutes = activity.map((item) => Number(item.minutes || 0));

  learningChart?.destroy();
  learningChart = new Chart(
    document.getElementById('learning-analytics-chart'),
    {
      type: 'line',
      data: {
        labels,
        datasets: [{
          label: 'Study minutes',
          data: minutes,
          borderColor: '#7567e8',
          backgroundColor: 'rgba(117, 103, 232, .14)',
          fill: true,
          tension: .35,
          pointRadius: 3,
        }],
      },
      options: {
        responsive: true,
        plugins: { legend: { display: true } },
        scales: {
          y: { beginAtZero: true, title: { display: true, text: 'Minutes' } },
          x: { title: { display: true, text: 'Date' } },
        },
      },
    },
  );

  courseChart?.destroy();
  courseChart = new Chart(
    document.getElementById('course-progress-chart'),
    {
      type: 'bar',
      data: {
        labels: courses.map((course) => course.title),
        datasets: [{
          label: 'Course completion %',
          data: courses.map((course) => Number(course.progress || 0)),
          backgroundColor: ['#7567e8', '#34b9aa', '#f1a84c'],
          borderRadius: 8,
        }],
      },
      options: {
        responsive: true,
        indexAxis: 'y',
        scales: { x: { beginAtZero: true, max: 100 } },
      },
    },
  );

  document.querySelector('[data-report="completed"]').textContent =
    report.summary?.lessons_completed ?? '—';
  document.querySelector('[data-report="mastery"]').textContent =
    `${report.summary?.average_mastery ?? 0}%`;
}

renderLearningAnalytics().catch((error) => {
  console.error(error);
  document.querySelector('#learning-analytics-chart').replaceWith(
    Object.assign(document.createElement('p'), {
      className: 'empty-state',
      textContent: 'Analytics are not available yet.',
    }),
  );
});
```

The current backend does not fabricate daily activity. If the chart should show a day-by-day line, add a real `daily_activity` aggregation to the analytics service, for example:

```json
{
  "daily_activity": [
    { "date": "2026-08-12", "minutes": 20 },
    { "date": "2026-08-13", "minutes": 40 }
  ]
}
```

## 2. Supabase role update SQL

The authoritative role for this Flask application is `public.users.role`, not a client-supplied role and not an untrusted browser value. First inspect the target user:

```sql
select
  id,
  email,
  name,
  role,
  requested_role,
  teacher_approval_status
from public.users
where lower(email) = lower('teacher@example.com');
```

### Grant Teacher

```sql
begin;

update public.users
set
  role = 'teacher',
  requested_role = null,
  teacher_approval_status = 'approved',
  updated_at = now()
where lower(email) = lower('teacher@example.com')
returning id, email, name, role, teacher_approval_status;

commit;
```

### Grant Admin

```sql
begin;

update public.users
set
  role = 'admin',
  requested_role = null,
  teacher_approval_status = 'approved',
  updated_at = now()
where lower(email) = lower('admin@example.com')
returning id, email, name, role, teacher_approval_status;

commit;
```

After changing a role, make the user sign out and sign in again. The backend reads the current user from the database on authenticated requests. Do not update `auth.users` metadata as a replacement for `public.users.role`. Use a service/admin-only SQL session, never expose these queries in the browser, and do not grant `owner` casually.

## 3. Flask route for MCQ and short-answer Exam Builder

The production route already follows this shape. It validates title, duration, attempt limit, question count, question type, prompt, options, and answer key before calling the database abstraction.

```python
from flask import Blueprint, request

from backend.api.auth import token_required
from backend.db import db
from backend.rbac import error_response, permission_required

exams_bp = Blueprint('exams', __name__)


def validate_exam(payload):
    if len(str(payload.get('title', '')).strip()) < 3:
        return 'title_invalid'

    duration = int(payload.get('duration_minutes', 20))
    attempts = int(payload.get('max_attempts', 3))
    questions = payload.get('questions', [])

    if not 5 <= duration <= 180:
        return 'duration_invalid'
    if not 1 <= attempts <= 10:
        return 'attempt_limit_invalid'
    if not 1 <= len(questions) <= 50:
        return 'questions_invalid'

    for question in questions:
        question_type = question.get('question_type', 'multiple_choice')
        if question_type not in {'multiple_choice', 'short_answer'}:
            return 'question_type_invalid'
        if len(str(question.get('prompt', '')).strip()) < 5:
            return 'question_invalid'
        if question_type == 'multiple_choice' and not isinstance(question.get('options'), list):
            return 'options_invalid'
        if not str(question.get('correct_answer', '')).strip():
            return 'answer_invalid'

    return None


@exams_bp.post('')
@token_required
@permission_required('exams.manage')
def create_exam(current_user):
    payload = request.get_json(silent=True) or {}
    error = validate_exam(payload)
    if error:
        return error_response(
            error,
            'The exam payload is invalid.',
            'Шалгалтын мэдээлэл буруу байна.',
            400,
        )

    exam = db.create_exam(payload, created_by=current_user['id'])
    return {'message': 'Exam created.', 'exam': exam}, 201
```

The student-facing start route must not return `correct_answer` or `explanation` before submission:

```python
@exams_bp.post('/<int:exam_id>/attempts')
@token_required
@permission_required('exams.attempt')
def start_exam(current_user, exam_id):
    if current_user.get('role') != 'student':
        return {'error': 'student_only'}, 403

    attempt, problem = db.start_exam(exam_id, current_user['id'])
    if problem == 'attempt_limit_reached':
        return {'error': 'attempt_limit_reached'}, 409
    if problem or not attempt:
        return {'error': problem or 'exam_not_available'}, 404
    return {'attempt': attempt}, 201
```

Answer autosave and final submit are separate endpoints:

```python
@exams_bp.patch('/attempts/<int:attempt_id>/answers/<int:question_id>')
@token_required
@permission_required('exams.attempt')
def save_answer(current_user, attempt_id, question_id):
    payload = request.get_json(silent=True) or {}
    attempt = db.get_attempt(attempt_id, user_id=current_user['id'], include_answers=False)
    if not attempt or attempt['status'] != 'in_progress':
        return {'error': 'attempt_closed'}, 409

    saved = db.save_exam_answer(
        attempt_id,
        question_id,
        str(payload.get('answer', ''))[:5000],
    )
    return {'answer': saved, 'saved': True}, 200


@exams_bp.post('/attempts/<int:attempt_id>/submit')
@token_required
@permission_required('exams.attempt')
def submit_exam(current_user, attempt_id):
    attempt, problem = db.submit_exam(attempt_id, current_user['id'])
    if problem or not attempt:
        return {'error': problem or 'attempt_not_found'}, 404
    return {'message': 'Exam submitted.', 'attempt': attempt}, 200
```

## 4. Supabase assessment schema

Apply this migration after the existing auth, learning platform, external identity, and lesson progress migrations:

```sql
alter table if exists public.exams
  add column if not exists duration_minutes integer not null default 20,
  add column if not exists max_attempts integer not null default 3,
  add column if not exists status text not null default 'published',
  add column if not exists updated_at timestamptz not null default now();

create table if not exists public.exam_questions (
  id bigint generated by default as identity primary key,
  exam_id bigint not null references public.exams(id) on delete cascade,
  problem_id bigint references public.problems(id) on delete set null,
  position integer not null default 1,
  question_type text not null default 'multiple_choice'
    check (question_type in ('multiple_choice', 'short_answer', 'code')),
  prompt text not null,
  options jsonb not null default '[]'::jsonb,
  correct_answer text,
  points numeric(8, 2) not null default 1 check (points > 0),
  explanation text not null default '',
  created_at timestamptz not null default now(),
  unique (exam_id, position)
);

create table if not exists public.exam_attempts (
  id bigint generated by default as identity primary key,
  exam_id bigint not null references public.exams(id) on delete cascade,
  user_id bigint not null references public.users(id) on delete cascade,
  status text not null default 'in_progress'
    check (status in ('in_progress', 'submitted', 'graded', 'expired')),
  score numeric(8, 2) not null default 0 check (score between 0 and 100),
  earned_points numeric(10, 2) not null default 0,
  total_points numeric(10, 2) not null default 0,
  started_at timestamptz not null default now(),
  submitted_at timestamptz,
  graded_at timestamptz,
  unique (exam_id, user_id, id)
);

create table if not exists public.exam_answers (
  id bigint generated by default as identity primary key,
  attempt_id bigint not null references public.exam_attempts(id) on delete cascade,
  question_id bigint not null references public.exam_questions(id) on delete cascade,
  answer text not null default '',
  is_correct boolean,
  earned_points numeric(10, 2) not null default 0,
  feedback text not null default '',
  updated_at timestamptz not null default now(),
  unique (attempt_id, question_id)
);

create index if not exists exam_questions_exam_position_idx
  on public.exam_questions (exam_id, position);
create index if not exists exam_attempts_user_status_idx
  on public.exam_attempts (user_id, status, started_at desc);
create index if not exists exam_answers_attempt_idx
  on public.exam_answers (attempt_id);
```

The actual project migration is `backend/db/migrations/005_assessments_and_progress.sql`. In the current UI, MCQ and short-answer questions are fully supported. The `code` type remains an extensibility option for a future integration with the existing sandbox/submission evaluator and should not be enabled in the current Builder without adding code-specific grading.

## 5. Useful API response boundary

A student-facing exam response must look like this before submission:

```json
{
  "id": 1,
  "title": "Python foundations checkpoint",
  "questions": [
    {
      "id": 1,
      "question_type": "multiple_choice",
      "prompt": "Which value is immutable in Python?",
      "options": ["list", "dictionary", "tuple", "set"],
      "points": 1
    }
  ]
}
```

There must be no `correct_answer` in that response. The answer key stays in the database/service layer and is used only during server-side grading.
