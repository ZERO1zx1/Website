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
│   │   └── index.html       # Main HTML template
│   └── static/
│       ├── css/
│       │   └── style.css    # Main stylesheet
│       └── js/
│           ├── app.js       # Frontend application
│           ├── monaco-editor.js
│           └── adapters/    # Mock/API adapter boundary
├── sandbox/
│   ├── runner.py            # Code execution runner
│   └── Dockerfile           # Sandbox container definition
├── tests/
│   ├── test_frontend_shell.py
│   └── test_code_executor.py
└── docs/                    # Design and integration handoff
```

## Frontend-first workflow

The current frontend prototype is intentionally complete before backend integration. It uses mock data through an adapter boundary in `frontend/static/js/app.js`, so screens and interactions can be reviewed without Supabase credentials. The design handoff is documented in [`docs/frontend-design-handoff.md`](docs/frontend-design-handoff.md).

To preview the frontend without loading backend blueprints:

```bash
FRONTEND_ONLY=true PYTHONPATH=. python -m flask --app 'app:create_app()' run --host 0.0.0.0 --port 5000
```

The frontend includes the dashboard, learning path, practice library, assessments, profile/preferences, responsive navigation, theme switching and a mock code editor flow. Backend integration is intentionally deferred until the frontend screens and Figma structure are approved.

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
- `POST /api/submissions` - Submit code for evaluation
- `GET /api/submissions/<submission_id>` - Get submission results
- `GET /api/submissions/user/<user_id>` - Get user's submissions

### Teacher
- `GET /api/teacher/classes` - Get teacher's classes
- `GET /api/teacher/classes/<class_id>/students` - Get class students
- `GET /api/teacher/analytics/class/<class_id>` - Get class analytics

### Analytics
- `GET /api/analytics/mastery/<user_id>` - Get user mastery
- `GET /api/analytics/skill/<skill_id>` - Get skill statistics
- `GET /api/analytics/problem/<problem_id>` - Get problem statistics

## Security Considerations

1. **Role Enforcement**: All role checks are performed server-side. Never trust client-provided role data.
2. **Code Sandbox**: Student code executes in isolated Docker containers with strict resource limits.
3. **Token Security**: JWT tokens are signed with a secret key and include expiration.
4. **Input Validation**: All user inputs are validated and sanitized.
5. **CORS**: Cross-Origin Resource Sharing is configured for security.
6. **SQL Injection**: Supabase client library handles parameterized queries.

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

Run tests with pytest:
```bash
pytest tests/
```

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
