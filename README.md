# Programming Learning Intelligence Platform

An elegant, polished, and fully-featured online coding education platform built with Python Flask, HTML/CSS/JavaScript, and Supabase.

## Features

### 1. Role-Based Authentication System
- Three roles: **Student**, **Teacher**, **Admin**
- Teacher accounts require admin approval before activation
- Server-side role enforcement (never trust client input)
- Secure JWT token-based authentication

### 2. Structured Curriculum Management
- **Courses**: Top-level course containers
- **Classes**: Teacher-led course instances with enrollment codes
- **Modules**: Logical groupings within courses
- **Lessons**: Individual learning units with content
- **Skills**: Competency tracking across the platform
- **Learning Objectives**: Mapping lessons to skills

### 3. Problem Bank
- Comprehensive problem repository with metadata:
  - Title, description, difficulty (easy/medium/hard)
  - Starter code and full solution
  - Visible and hidden test cases
  - Hints with progressive levels
  - Explanations and full version history
- Multi-language support (Python, JavaScript, C++, Java)

### 4. Secure Code Execution Sandbox
- Isolated Docker container execution
- Resource limits: CPU, memory, timeout, network restrictions
- Asynchronous submission processing
- Comprehensive error classification
- No code execution in main web process

### 5. Four Learning Modes
- **Learn**: Guided lesson experience with hints
- **Practice**: Progressive feedback loops with unlimited attempts
- **Exam**: Restricted summative assessment with time limits
- **Challenge**: Optional quest-style problems

### 6. Monaco Editor Integration
- Syntax highlighting for multiple languages
- Theme selection (light, dark, high contrast)
- Font size controls and keyboard shortcuts
- Autosave functionality
- Reset to starter code button
- Run code shortcut (Ctrl+Enter / Cmd+Enter)
- Submit code shortcut (Ctrl+Shift+Enter / Cmd+Shift+Enter)

### 7. Mastery Tracking
- Per-skill mastery scores (0-100)
- Four signals: first-attempt success rate, retry recovery, hint usage, problem difficulty
- Real-time progress visualization
- Skill heatmaps for classes

### 8. Real-Time Teacher Dashboards
- Class overview with student progress
- Real-time student monitoring (states: reading, coding, testing, submitted, stuck)
- Intervention queue for students needing help
- Skill heatmaps (students × skills mastery matrix)
- Problem analytics (difficulty, completion rate, common errors)
- Class-wide analytics and mastery trends

### 9. Exam Builder
- Comprehensive exam creation wizard
- Problem selection with preview
- Configurable rules: time limits, attempt limits, randomization
- Scoring and rubric configuration
- Scheduled start/end times
- Partial credit and hidden test support

### 10. Socratic AI Tutor
- Conceptual hints and guided questions
- Never reveals direct answers
- Error explanation in educational terms
- Conversation history tracking
- Teacher-configurable AI assistance policies

### 11. Automated Problem Generator
- Problem description generation from title
- Test case generation
- Rubric criteria generation
- Hint generation for common mistakes
- Solution explanation generation

### 12. Notifications
- Assignment published notifications
- Deadline approaching alerts
- Exam scheduled notifications
- Teacher feedback available alerts
- User-configurable notification preferences

## Project Structure

```
programming-learning-platform/
├── app.py                    # Flask application factory
├── backend/
│   ├── __init__.py
│   ├── db.py                 # Supabase database client
│   ├── api/
│   │   ├── __init__.py
│   │   ├── auth.py           # Authentication and RBAC
│   │   ├── courses.py        # Course management
│   │   ├── problems.py       # Problem bank
│   │   ├── submissions.py    # Code submissions and evaluation
│   │   ├── teacher.py        # Teacher dashboard
│   │   └── analytics.py      # Analytics and reporting
│   └── services/
│       ├── __init__.py
│       ├── code_executor.py  # Docker sandbox executor
│       └── submission_evaluator.py
├── requirements.txt          # Python dependencies
├── frontend/
│   ├── templates/
│   │   ├── index.html                 # Full learning workspace
│   │   └── pages/                     # Separate public/auth/dashboard pages
│   │       ├── base.html
│   │       ├── home.html
│   │       ├── login.html
│   │       ├── register.html
│   │       ├── password_reset.html
│   │       └── dashboard.html
│   └── static/
│       ├── css/
│       │   ├── style.css              # Workspace design system
│       │   └── site/site.css           # Shared multi-page site styling
│       ├── js/
│       │   ├── app.js                 # Full learning workspace
│       │   ├── pages/auth.js          # Auth/recovery/dashboard page logic
│       │   ├── modules/monaco-editor.js
│       │   └── adapters/              # Live API adapter boundary
│       └── assets/                    # images, icons, and fonts
├── ci/
│   ├── check.sh                       # Canonical local/CI quality gate
│   └── validate_frontend_structure.py
├── .github/workflows/ci.yml           # GitHub Actions quality pipeline
├── sandbox/
│   ├── runner.py            # Code execution runner
│   └── Dockerfile           # Sandbox container definition
├── tests/
│   ├── test_frontend_shell.py
│   └── test_code_executor.py
└── docs/                    # Design and integration handoff
```

## Development modes and full-stack integration

The frontend is served by Flask in both supported modes. `FRONTEND_ONLY=true` is an explicitly labelled demo mode for UI review without Supabase credentials; it may use local fixtures and a simulated editor flow. Normal backend mode (`FRONTEND_ONLY=false`) uses the live API adapter for authentication, dashboard data, courses, problems, visible-test execution, graded submissions, SSE submission updates, and polling fallback. A failed live request remains an error state and is never silently replaced with believable mock data.

To preview the labelled frontend-only mode:

```bash
FRONTEND_ONLY=true PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000
```

For local backend mode, set `FRONTEND_ONLY=false` and start Flask with `PYTHONPATH=. python app.py`. When Supabase credentials are absent in development, the application automatically uses a file-backed SQLite database at `instance/codehaven.sqlite3` (or `LOCAL_DB_PATH`), seeds real courses and problems, and persists registration, login, learning records, and submissions across requests and restarts. To use Supabase locally, provide `SUPABASE_URL` and `SUPABASE_KEY` in `.env`; apply migrations in numeric order (`001_auth_roles.sql`, `002_learning_platform.sql`, `003_external_auth_identities.sql`), then optionally apply `backend/db/seed/001_demo_content.sql`. Production still requires Supabase, a strong `SECRET_KEY`, a non-empty `SANDBOX_TOKEN` when the sandbox is enabled, and `REDIS_URL` when Redis queue mode is selected.

## Backend stack and role model

The backend uses Python and Flask for the application/API layer, SQLite for credential-free local development, Supabase for production persistence, Docker for the web and isolated code execution environments, YAML for role/configuration data, and Markdown for architecture and integration handoff documentation.

The supported roles are `owner` (**эзэмшигч**), `admin` (**администратор**), `teacher` (**багш**) and `student` (**суралцагч**). The owner is the highest platform role and can manage owner-level role assignments. Administrators manage operational resources and teacher approvals. Teachers manage their assigned classes and content. Students access their own learning, submissions and progress. The authoritative matrix is in [`docs/role-permission-spec.md`](docs/role-permission-spec.md), and the machine-readable policy is in [`config/roles.yml`](config/roles.yml).

Backend work is intentionally sequenced as authentication, current user, dashboard, learning path, problems, teacher panel and submissions. Each integration preserves the frontend adapter contract and adds loading, empty, error and unauthorized states before moving to the next group.

For a local container run, configure `.env` and use:

```bash
docker compose up --build
```

The backend runbook is documented in [`docs/backend-integration.md`](docs/backend-integration.md), the complete Supabase Email/Google and local backend setup is in [`docs/supabase-and-local-backend.md`](docs/supabase-and-local-backend.md), the training assessment flow is in [`docs/training-assessments.md`](docs/training-assessments.md), and the project layout is in [`docs/project-structure.md`](docs/project-structure.md). Apply migrations `001` through `005_assessments_and_progress.sql` in order for production Supabase.

## Installation

### Prerequisites
- Python 3.8+
- Supabase account
- Docker (for code sandbox)
- Redis (optional, for job queue)

### Setup

1. **Clone the repository**
```bash
git clone <repository-url>
cd programming-learning-platform
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your Supabase credentials and other settings
```

4. **Run the application**
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login and get JWT token
- `POST /api/auth/password-reset/request` - Request password recovery
- `POST /api/auth/password-reset/confirm` - Consume a local reset token
- `POST /api/auth/otp/request` - Request Supabase email OTP
- `POST /api/auth/otp/verify` - Verify Supabase email OTP
- `GET /api/auth/google/start` - Start Google OAuth
- `GET /api/auth/me` - Get current user info
- `POST /api/auth/request-teacher-role` - Request teacher role
- `POST /api/auth/approve-teacher/<user_id>` - Admin: Approve teacher
- `POST /api/auth/reject-teacher/<user_id>` - Admin: Reject teacher

### Courses
- `GET /api/courses` - List all courses
- `POST /api/courses` - Create new course (teacher only)
- `GET /api/courses/<course_id>` - Get course details
- `PUT /api/courses/<course_id>` - Update course (teacher only)
- `DELETE /api/courses/<course_id>` - Delete course (teacher only)

### Problems
- `GET /api/problems` - List all problems
- `POST /api/problems` - Create new problem (teacher only)
- `GET /api/problems/<problem_id>` - Get problem details
- `PUT /api/problems/<problem_id>` - Update problem (teacher only)
- `DELETE /api/problems/<problem_id>` - Delete problem (teacher only)

### Submissions
- `POST /api/submissions/run` - Run code against visible tests without creating a graded submission
- `POST /api/submissions` - Submit code for asynchronous evaluation
- `GET /api/submissions/<submission_id>` - Get an authorized submission and non-sensitive results
- `GET /api/submissions/<submission_id>/stream` - Stream submission status over SSE
- `GET /api/submissions/user/<user_id>` - Get an authorized user's submissions

### Teacher
- `GET /api/teacher/classes` - Get teacher's classes
- `GET /api/teacher/classes/<class_id>/students` - Get class students
- `GET /api/teacher/analytics/class/<class_id>` - Get class analytics

### Analytics
- `GET /api/analytics/dashboard` - Get authenticated dashboard, exam summary, and progress report
- `GET /api/analytics/progress-report` - Get course, lesson, mastery, and exam progress report
- `GET /api/analytics/mastery/<user_id>` - Get user mastery
- `GET /api/analytics/skill/<skill_id>` - Get skill statistics
- `GET /api/analytics/problem/<problem_id>` - Get problem statistics

### Training assessments
- `GET /api/exams` - List published exams and learner attempt summaries
- `POST /api/exams` - Create an exam and questions for teacher/admin/owner roles
- `GET /api/exams/<exam_id>` - Get exam detail with answer keys restricted to staff
- `POST /api/exams/<exam_id>/attempts` - Start or resume a student attempt
- `GET /api/exams/attempts/<attempt_id>` - Get an owned or authorized attempt
- `PATCH /api/exams/attempts/<attempt_id>/answers/<question_id>` - Autosave an answer
- `POST /api/exams/attempts/<attempt_id>/submit` - Submit and grade an attempt
- `GET /api/exams/<exam_id>/report` - Get scoped aggregate exam report

## Security Considerations

1. **Role Enforcement**: All role checks are performed server-side. Never trust client-provided role data.
2. **Code Sandbox**: Student code executes through the internal sandbox service, never directly in the Flask web process. Docker applies non-root execution, resource limits, no network, read-only filesystems, dropped capabilities, and no-new-privileges.
3. **Sandbox Authentication**: Production Compose requires `SANDBOX_TOKEN`; there is no known default token, and the sandbox refuses unauthenticated production startup.
4. **Token Security**: JWT tokens are signed with a secret key and include expiration. Browser sessions use session storage and remove legacy local-storage tokens during migration.
5. **Input Validation**: All user inputs and request sizes are validated server-side. Hidden test inputs and expected outputs are filtered from student submission responses and streams.
6. **CORS and Headers**: CORS origins are explicit and production security headers include CSP, clickjacking protection, MIME sniffing protection, and secure referrer policy.
7. **SQL Injection**: Supabase client library handles parameterized queries.
8. **Readiness**: `/api/health` reports process liveness; `/api/ready` checks configuration and, when enabled, Supabase, Redis, and sandbox availability.

## Development

### Adding a New Route

1. Create a new file in `backend/api/` directory
2. Define your blueprint with Flask
3. Register it in `app.py`
4. Add appropriate decorators for authentication and role enforcement

Example:
```python
from flask import Blueprint, request, jsonify
from backend.api.auth import token_required, role_required

my_bp = Blueprint('my_feature', __name__)

@my_bp.route('/my-endpoint', methods=['GET'])
@token_required
def my_endpoint(current_user):
    # Your logic here
    return {'data': 'value'}, 200
```

### Testing
Run the canonical CI gate locally. It is the same deterministic check invoked by GitHub Actions and covers Python compilation, the full test suite, all frontend JavaScript modules, frontend structure, Compose topology, and repository hygiene.

```bash
bash ci/check.sh
```

For a focused manual check:

```bash
PYTHONPATH=. pytest -q
python3 -m compileall -q .
node --check frontend/static/js/pages/auth.js
node --check frontend/static/js/modules/monaco-editor.js
git diff --check
```

Docker validation requires Docker Engine:

```bash
docker compose config
docker compose build
docker compose up
```

Compose requires a populated local `.env` with a strong `SANDBOX_TOKEN`; Redis and sandbox ports are not published to the host.

## Deployment

### Production Checklist
- [ ] Set `FLASK_ENV=production`
- [ ] Use strong `SECRET_KEY`
- [ ] Configure HTTPS
- [ ] Set up proper logging
- [ ] Configure database backups
- [ ] Set up monitoring and alerts
- [ ] Review security settings
- [ ] Load test the application

### Deployment Options
- Heroku
- AWS EC2 / ECS
- Google Cloud Platform
- DigitalOcean
- Docker + Kubernetes

## Contributing

1. Create a feature branch
2. Make your changes
3. Write tests
4. Submit a pull request

## License

MIT License

## Support

For issues and questions, please open an issue on the repository.

## Roadmap

- [ ] Mobile app (React Native)
- [ ] Real-time collaboration features
- [ ] Advanced AI tutoring
- [ ] Gamification system
- [ ] Integration with popular IDEs
- [ ] API for third-party integrations
