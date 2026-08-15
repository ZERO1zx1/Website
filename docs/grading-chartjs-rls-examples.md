# Exam Auto-Grading, Chart.js Grade Analytics, and Supabase RLS

This guide matches the Codehaven assessment contract: MCQ and short-answer questions are graded server-side, `exam_questions` stores the answer key, `exam_attempts` stores one learner's attempt, and `exam_answers` stores autosaved/submitted answers.

## 1. Flask auto-grading logic

The browser must never calculate the final score and must never send the answer key back as an authority. The server loads the exam question keys, normalizes the learner answer, grades each answer, updates `exam_answers`, and then updates `exam_attempts` in one transaction or equivalent atomic service operation.

```python
from datetime import datetime, timezone


def normalize_answer(value: str) -> str:
    """Normalize harmless whitespace/case differences for text answers."""
    return " ".join(str(value or "").strip().casefold().split())


def grade_attempt(attempt: dict, questions: list[dict], answers: list[dict]) -> dict:
    answers_by_question = {
        int(answer["question_id"]): answer for answer in answers
    }
    earned_points = 0.0
    total_points = 0.0
    graded_answers = []

    for question in questions:
        question_id = int(question["id"])
        points = float(question.get("points") or 1)
        expected = normalize_answer(question.get("correct_answer"))
        actual = normalize_answer(
            answers_by_question.get(question_id, {}).get("answer", "")
        )
        is_correct = bool(expected) and actual == expected
        earned = points if is_correct else 0.0
        earned_points += earned
        total_points += points

        graded_answers.append({
            "attempt_id": attempt["id"],
            "question_id": question_id,
            "answer": answers_by_question.get(question_id, {}).get("answer", ""),
            "is_correct": is_correct,
            "earned_points": earned,
            "feedback": question.get("explanation", ""),
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })

    score = round((earned_points / total_points) * 100, 2) if total_points else 0
    return {
        "answers": graded_answers,
        "score": score,
        "earned_points": earned_points,
        "total_points": total_points,
        "status": "graded",
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "graded_at": datetime.now(timezone.utc).isoformat(),
    }
```

A Flask route should verify ownership and attempt state before calling the grader:

```python
@exams_bp.post('/attempts/<int:attempt_id>/submit')
@token_required
@permission_required('exams.attempt')
def submit_exam(current_user, attempt_id):
    attempt = db.get_attempt(
        attempt_id,
        user_id=current_user['id'],
        include_answers=True,
    )
    if not attempt:
        return {'error': 'attempt_not_found'}, 404
    if attempt['status'] != 'in_progress':
        return {'attempt': attempt, 'already_submitted': True}, 200

    if db.attempt_is_expired(attempt):
        result = db.grade_and_close_attempt(
            attempt,
            status='expired',
        )
    else:
        result = db.grade_and_close_attempt(
            attempt,
            status='graded',
        )

    return {'message': 'Exam submitted.', 'attempt': result}, 200
```

The database service should use a transaction when available. The important invariant is that the answer rows and attempt summary cannot partially update. In the existing project, `SupabaseDB.submit_exam()` performs the same flow through the database wrapper and updates `exam_answers` before updating the owned `exam_attempts` row.

For MCQ, `correct_answer` is compared with the selected option. For short-answer, the example normalizes leading/trailing whitespace, repeated spaces, and case. Do not use fuzzy matching for graded answers unless the teacher explicitly configures an accepted-answer set; fuzzy matching can award credit to an unintended answer.

## 2. Chart.js grade distribution

Teacher/admin exam reports are returned by `GET /api/exams/<exam_id>/report` and include:

```json
{
  "average_score": 76.5,
  "highest_score": 100,
  "pass_rate": 75,
  "distribution": {
    "excellent": 4,
    "pass": 5,
    "needs_review": 3
  }
}
```

A doughnut chart for a teacher dashboard can use that real response:

```html
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.4/dist/chart.umd.min.js"></script>
<canvas id="grade-distribution-chart" aria-label="Grade distribution"></canvas>
<canvas id="score-history-chart" aria-label="Student score history"></canvas>
```

```javascript
const token = sessionStorage.getItem('codehaven-access-token');

async function getExamReport(examId) {
  const response = await fetch(`/api/exams/${examId}/report`, {
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${token}`,
    },
  });
  if (!response.ok) throw new Error('Exam report could not be loaded.');
  return (await response.json()).report;
}

let distributionChart;

async function renderTeacherGradeDistribution(examId) {
  const report = await getExamReport(examId);
  const distribution = report.distribution || {};

  distributionChart?.destroy();
  distributionChart = new Chart(
    document.getElementById('grade-distribution-chart'),
    {
      type: 'doughnut',
      data: {
        labels: ['Excellent (80–100)', 'Pass (60–79)', 'Needs review (<60)'],
        datasets: [{
          data: [
            Number(distribution.excellent || 0),
            Number(distribution.pass || 0),
            Number(distribution.needs_review || 0),
          ],
          backgroundColor: ['#34b9aa', '#7567e8', '#ef8b74'],
          borderWidth: 0,
        }],
      },
      options: {
        responsive: true,
        plugins: {
          legend: { position: 'bottom' },
          tooltip: {
            callbacks: {
              label: (context) => `${context.label}: ${context.raw}`,
            },
          },
        },
      },
    },
  );
}
```

A student dashboard should show only that student's score history, not the class distribution. If the progress endpoint returns `exams` ordered by attempt date, render a line chart:

```javascript
function renderStudentScoreHistory(report) {
  const attempts = (report.exams || [])
    .filter((attempt) => ['graded', 'submitted', 'expired'].includes(attempt.status))
    .slice()
    .reverse();

  new Chart(document.getElementById('score-history-chart'), {
    type: 'line',
    data: {
      labels: attempts.map((attempt) =>
        new Date(attempt.submitted_at || attempt.started_at).toLocaleDateString()),
      datasets: [{
        label: 'My exam score',
        data: attempts.map((attempt) => Number(attempt.score || 0)),
        borderColor: '#7567e8',
        backgroundColor: 'rgba(117, 103, 232, .12)',
        fill: true,
        tension: .3,
      }],
    },
    options: {
      responsive: true,
      scales: { y: { beginAtZero: true, max: 100 } },
    },
  });
}
```

Never put teacher aggregate data in a student response. The backend should choose the response shape based on the authenticated role and ownership.

## 3. Supabase helper functions for RLS

The browser's Supabase session contains an Auth UUID, while this project stores the local role record in `public.users`. The helper functions bridge `auth.uid()` to `public.users.auth_user_id`.

```sql
create or replace function public.current_app_user_id()
returns bigint
language sql
stable
security definer
set search_path = public
as $$
  select id
  from public.users
  where auth_user_id = auth.uid()
  limit 1;
$$;

create or replace function public.current_app_role()
returns text
language sql
stable
security definer
set search_path = public
as $$
  select role
  from public.users
  where auth_user_id = auth.uid()
  limit 1;
$$;
```

The functions should be callable by the authenticated database role but not writable by clients:

```sql
revoke all on function public.current_app_user_id() from public;
revoke all on function public.current_app_role() from public;
grant execute on function public.current_app_user_id() to authenticated;
grant execute on function public.current_app_role() to authenticated;
```

## 4. RLS for exam questions

Enable RLS and allow staff to manage questions for their own exams. Students can read questions only when the exam is published.

```sql
alter table public.exam_questions enable row level security;
alter table public.exam_questions force row level security;

create policy "published exam questions are readable by students"
on public.exam_questions
for select
to authenticated
using (
  exists (
    select 1
    from public.exams e
    where e.id = exam_questions.exam_id
      and e.status = 'published'
  )
  and public.current_app_role() = 'student'
);

create policy "staff can read managed exam questions"
on public.exam_questions
for select
to authenticated
using (
  public.current_app_role() in ('owner', 'admin')
  or (
    public.current_app_role() = 'teacher'
    and exists (
      select 1
      from public.exams e
      where e.id = exam_questions.exam_id
        and e.created_by = public.current_app_user_id()
    )
  )
);

create policy "staff can create exam questions"
on public.exam_questions
for insert
to authenticated
with check (
  public.current_app_role() in ('owner', 'admin')
  or (
    public.current_app_role() = 'teacher'
    and exists (
      select 1
      from public.exams e
      where e.id = exam_questions.exam_id
        and e.created_by = public.current_app_user_id()
    )
  )
);

create policy "staff can update managed exam questions"
on public.exam_questions
for update
to authenticated
using (
  public.current_app_role() in ('owner', 'admin')
  or (
    public.current_app_role() = 'teacher'
    and exists (
      select 1
      from public.exams e
      where e.id = exam_questions.exam_id
        and e.created_by = public.current_app_user_id()
    )
  )
)
with check (
  public.current_app_role() in ('owner', 'admin')
  or (
    public.current_app_role() = 'teacher'
    and exists (
      select 1
      from public.exams e
      where e.id = exam_questions.exam_id
        and e.created_by = public.current_app_user_id()
    )
  )
);
```

### Important column-redaction warning

RLS controls rows, not columns. If students can select the raw `exam_questions` table, a policy that allows a published question row can still expose `correct_answer` and `explanation`. The safest options are:

1. Keep the raw table private to the Flask service and let the backend remove answer keys, which is the current Codehaven pattern.
2. Expose a separate student-safe table or view containing only `id`, `exam_id`, `position`, `question_type`, `prompt`, `options`, and `points.
3. Store answer keys in a separate `exam_question_keys` table accessible only to the grading service.

For a direct Supabase client, a safe view should be used only after verifying the Postgres/Supabase version's view security behavior and applying RLS to the underlying table:

```sql
create or replace view public.student_exam_questions
with (security_invoker = true)
as
select
  id,
  exam_id,
  position,
  question_type,
  prompt,
  options,
  points
from public.exam_questions;
```

Do not select `correct_answer` from a student-facing API response.

## 5. RLS for student attempts

Students can create and read only their own attempts. They can update an in-progress attempt, but cannot change a graded or expired attempt. Staff can read attempts for exams they own; owner/admin can read all attempts.

```sql
alter table public.exam_attempts enable row level security;
alter table public.exam_attempts force row level security;

create policy "students read their own attempts"
on public.exam_attempts
for select
to authenticated
using (
  user_id = public.current_app_user_id()
  and public.current_app_role() = 'student'
);

create policy "students create their own attempts"
on public.exam_attempts
for insert
to authenticated
with check (
  user_id = public.current_app_user_id()
  and public.current_app_role() = 'student'
  and exists (
    select 1
    from public.exams e
    where e.id = exam_attempts.exam_id
      and e.status = 'published'
  )
);

create policy "students update their own active attempts"
on public.exam_attempts
for update
to authenticated
using (
  user_id = public.current_app_user_id()
  and public.current_app_role() = 'student'
  and status = 'in_progress'
)
with check (
  user_id = public.current_app_user_id()
  and public.current_app_role() = 'student'
);

create policy "staff read managed attempts"
on public.exam_attempts
for select
to authenticated
using (
  public.current_app_role() in ('owner', 'admin')
  or (
    public.current_app_role() = 'teacher'
    and exists (
      select 1
      from public.exams e
      where e.id = exam_attempts.exam_id
        and e.created_by = public.current_app_user_id()
    )
  )
);
```

For strict production security, do not let a student update `score`, `earned_points`, `total_points`, `graded_at`, or `submitted_at` directly. Put grading and closing behind the Flask service or a locked-down Postgres function. RLS is an important boundary, but it is not a substitute for server-side validation and answer-key redaction.

## 6. RLS for exam answers

```sql
alter table public.exam_answers enable row level security;
alter table public.exam_answers force row level security;

create policy "students read answers from their own attempts"
on public.exam_answers
for select
to authenticated
using (
  exists (
    select 1
    from public.exam_attempts a
    where a.id = exam_answers.attempt_id
      and a.user_id = public.current_app_user_id()
  )
);

create policy "students write answers to their active attempts"
on public.exam_answers
for insert
 to authenticated
with check (
  exists (
    select 1
    from public.exam_attempts a
    where a.id = exam_answers.attempt_id
      and a.user_id = public.current_app_user_id()
      and a.status = 'in_progress'
  )
);

create policy "students update answers to their active attempts"
on public.exam_answers
for update
to authenticated
using (
  exists (
    select 1
    from public.exam_attempts a
    where a.id = exam_answers.attempt_id
      and a.user_id = public.current_app_user_id()
      and a.status = 'in_progress'
  )
)
with check (
  exists (
    select 1
    from public.exam_attempts a
    where a.id = exam_answers.attempt_id
      and a.user_id = public.current_app_user_id()
      and a.status = 'in_progress'
  )
);
```

The grading service can use a controlled server-side connection or a narrowly scoped function to write `is_correct`, `earned_points`, and `feedback` after submission. Test the policies with two student accounts, a teacher who owns an exam, a teacher who does not own it, and an admin/owner account.
