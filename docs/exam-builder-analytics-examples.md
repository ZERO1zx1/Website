# Dashboard Analytics and Exam Builder Examples

These examples match the Codehaven Flask API contract. The production implementation lives in `frontend/templates/pages/workspace_dashboard.html`, `frontend/templates/pages/assessments.html`, `frontend/static/js/app.js`, and `frontend/static/js/adapters/api-adapter.js`.

## 1. Dashboard progress report

The dashboard requests real authenticated data instead of using a fixture:

```javascript
async function loadDashboardReport() {
  const dashboardResponse = await fetch('/api/analytics/dashboard', {
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${sessionStorage.getItem('codehaven-access-token')}`,
    },
  });

  if (!dashboardResponse.ok) {
    throw new Error('Dashboard data could not be loaded.');
  }

  const dashboard = await dashboardResponse.json();
  const report = dashboard.progress_report || {};
  const summary = report.summary || {};

  document.querySelector('[data-report="completed"]').textContent =
    summary.lessons_completed ?? '—';
  document.querySelector('[data-report="active"]').textContent =
    summary.courses_active ?? '—';
  document.querySelector('[data-report="mastery"]').textContent =
    `${summary.average_mastery ?? 0}%`;
  document.querySelector('[data-report="exam-score"]').textContent =
    dashboard.exam_summary?.best_score == null
      ? '—'
      : `${dashboard.exam_summary.best_score}%`;
}
```

A report response has this shape:

```json
{
  "summary": {
    "lessons_started": 2,
    "lessons_completed": 1,
    "courses_active": 2,
    "average_mastery": 68
  },
  "courses": [
    {
      "id": 1,
      "title": "Python foundations",
      "progress": 50,
      "completed_lessons": 1,
      "lesson_count": 2
    }
  ],
  "exams": [
    {
      "id": 1,
      "exam_id": 1,
      "status": "graded",
      "score": 82
    }
  ],
  "mastery": []
}
```

## 2. Exam Builder HTML

The Builder is shown only to users with `teacher`, `admin`, or `owner` role. The server still enforces this permission; hiding a button is not a security control.

```html
<form id="exam-builder-form">
  <label>
    Exam title
    <input name="title" required minlength="3"
           placeholder="Python foundations checkpoint">
  </label>

  <label>
    Duration in minutes
    <input name="duration_minutes" type="number"
           min="5" max="180" value="20" required>
  </label>

  <label>
    Maximum attempts
    <input name="max_attempts" type="number"
           min="1" max="10" value="3" required>
  </label>

  <label>
    Description
    <textarea name="description" rows="3"></textarea>
  </label>

  <div id="question-list"></div>
  <button type="button" id="add-question">Add question</button>
  <button type="submit">Publish exam</button>
  <p id="builder-message" role="status"></p>
</form>
```

## 3. MCQ and short-answer question JavaScript

Each question contains a type selector. For an MCQ, options are entered one per line. For a short-answer question, options are hidden and the answer key is a text value.

```javascript
const questionList = document.querySelector('#question-list');
const builderForm = document.querySelector('#exam-builder-form');
let questionNumber = 0;

function addQuestion() {
  questionNumber += 1;
  const card = document.createElement('fieldset');
  card.className = 'builder-question-card';
  card.dataset.question = questionNumber;
  card.innerHTML = `
    <legend>Question ${questionNumber}</legend>

    <label>
      Type
      <select data-field="question_type">
        <option value="multiple_choice">Multiple choice</option>
        <option value="short_answer">Short answer</option>
      </select>
    </label>

    <label>
      Prompt
      <textarea data-field="prompt" required minlength="5"></textarea>
    </label>

    <label data-options-field>
      Options
      <textarea data-field="options"
        placeholder="One option per line"></textarea>
    </label>

    <label>
      Correct answer
      <input data-field="correct_answer" required>
    </label>

    <label>
      Points
      <input data-field="points" type="number" min="1" value="1" required>
    </label>

    <label>
      Explanation
      <textarea data-field="explanation" rows="2"></textarea>
    </label>

    <button type="button" data-remove>Remove</button>
  `;

  const typeSelect = card.querySelector('[data-field="question_type"]');
  const optionsField = card.querySelector('[data-options-field]');

  function updateType() {
    const isMultipleChoice = typeSelect.value === 'multiple_choice';
    optionsField.hidden = !isMultipleChoice;
    optionsField.querySelector('textarea').required = isMultipleChoice;
  }

  typeSelect.addEventListener('change', updateType);
  card.querySelector('[data-remove]').addEventListener('click', () => card.remove());
  questionList.append(card);
  updateType();
}

function readQuestion(card, position) {
  const read = (name) => card.querySelector(`[data-field="${name}"]`).value.trim();
  const type = read('question_type');

  return {
    position,
    question_type: type,
    prompt: read('prompt'),
    options: type === 'multiple_choice'
      ? read('options').split(/\r?\n/).map((item) => item.trim()).filter(Boolean)
      : [],
    correct_answer: read('correct_answer'),
    points: Number(read('points') || 1),
    explanation: read('explanation'),
  };
}

async function publishExam(event) {
  event.preventDefault();
  const formData = new FormData(builderForm);
  const questions = [...questionList.querySelectorAll('[data-question]')]
    .map((card, index) => readQuestion(card, index + 1));

  if (!questions.length) {
    throw new Error('Add at least one question.');
  }

  const payload = {
    title: formData.get('title').trim(),
    description: formData.get('description').trim(),
    duration_minutes: Number(formData.get('duration_minutes')),
    max_attempts: Number(formData.get('max_attempts')),
    questions,
  };

  const response = await fetch('/api/exams', {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      'Content-Type': 'application/json',
      Authorization: `Bearer ${sessionStorage.getItem('codehaven-access-token')}`,
    },
    body: JSON.stringify(payload),
  });

  const result = await response.json();
  if (!response.ok) {
    throw new Error(result.error?.message || 'Exam could not be created.');
  }

  document.querySelector('#builder-message').textContent = 'Exam published.';
  builderForm.reset();
  questionList.replaceChildren();
  questionNumber = 0;
  addQuestion();
}

document.querySelector('#add-question').addEventListener('click', addQuestion);
builderForm.addEventListener('submit', (event) => {
  publishExam(event).catch((error) => {
    document.querySelector('#builder-message').textContent = error.message;
  });
});

addQuestion();
```

For the current API, the following payload creates one MCQ and one short-answer question:

```json
{
  "title": "Python foundations checkpoint",
  "description": "Variables and functions practice",
  "duration_minutes": 20,
  "max_attempts": 3,
  "questions": [
    {
      "position": 1,
      "question_type": "multiple_choice",
      "prompt": "Which value is immutable in Python?",
      "options": ["list", "dictionary", "tuple", "set"],
      "correct_answer": "tuple",
      "points": 1,
      "explanation": "Tuples cannot be changed after creation."
    },
    {
      "position": 2,
      "question_type": "short_answer",
      "prompt": "Name the built-in function used to get a sequence length.",
      "options": [],
      "correct_answer": "len",
      "points": 1,
      "explanation": "len() returns the number of items."
    }
  ]
}
```

## 4. Student Exam View and progress signal

The Student Exam View starts an attempt, saves answers, and submits the attempt through the backend:

```javascript
async function startExam(examId) {
  const response = await fetch(`/api/exams/${examId}/attempts`, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${sessionStorage.getItem('codehaven-access-token')}`,
    },
  });
  return (await response.json()).attempt;
}

async function saveAnswer(attemptId, questionId, answer) {
  await fetch(`/api/exams/attempts/${attemptId}/answers/${questionId}`, {
    method: 'PATCH',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${sessionStorage.getItem('codehaven-access-token')}`,
    },
    body: JSON.stringify({ answer }),
  });
}

async function submitExam(attemptId) {
  const response = await fetch(`/api/exams/attempts/${attemptId}/submit`, {
    method: 'POST',
    headers: {
      Accept: 'application/json',
      Authorization: `Bearer ${sessionStorage.getItem('codehaven-access-token')}`,
    },
  });
  if (!response.ok) throw new Error('Exam submission failed.');
  return (await response.json()).attempt;
}
```

After `submitExam()` resolves, request `/api/analytics/progress-report` or refresh `/api/analytics/dashboard`. The response is then rendered into the result panel, so the student sees exam score, completed lessons, average mastery, saved attempt count, and course progress from the authenticated backend.
