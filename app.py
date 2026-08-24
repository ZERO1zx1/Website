"""
Programming Learning Intelligence Platform
Flask Application Factory
"""

import os

import requests
from dotenv import load_dotenv
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_login import LoginManager

from course_data import COURSE_CATALOG
from learning_experiences import LEARNING_PATH_NODES, PROJECT_CATALOG, PRACTICE_CHALLENGES, get_challenge, get_project
from backend.services.content_catalog import load_challenges


class FlaskSessionUser:
    """Minimal Flask-Login user wrapper for the JWT-backed database record."""

    def __init__(self, record):
        self.record = record
        self.id = record.get('id')
        self.name = record.get('name')
        self.email = record.get('email')
        self.role = record.get('role', 'student')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

# Load environment variables
load_dotenv()

def create_app(config_name='development'):
    """Application factory function"""
    app = Flask(
        __name__,
        template_folder='frontend/templates',
        static_folder='frontend/static',
    )
    
    # Configuration
    environment = os.getenv('FLASK_ENV', config_name or 'development').lower()
    secret_key = os.getenv('SECRET_KEY')
    if environment == 'production' and not secret_key:
        raise RuntimeError('SECRET_KEY must be set when FLASK_ENV=production')
    app.config['ENVIRONMENT'] = environment
    app.config['SECRET_KEY'] = secret_key or 'dev-secret-key-change-in-production'
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 256 * 1024))
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SECURE'] = environment == 'production'
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    frontend_only = os.getenv('FRONTEND_ONLY', 'false').lower() == 'true'
    app.config['FRONTEND_ONLY'] = frontend_only
    
    # CORS is explicit and environment-controlled; wildcard is not used by default.
    cors_origins = [
        origin.strip()
        for origin in os.getenv('CORS_ORIGINS', 'http://localhost:5000,http://127.0.0.1:5000').split(',')
        if origin.strip()
    ]
    app.config['CORS_ORIGINS'] = cors_origins
    CORS(app, resources={
        r"/api/*": {
            "origins": cors_origins,
            "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization", "Accept-Language"]
        }
    })

    @app.before_request
    def protect_cookie_authenticated_writes():
        """Reject cross-site state changes when a browser sends the session cookie."""
        if request.method in {'POST', 'PUT', 'PATCH', 'DELETE'} and request.cookies.get('codecraft_session'):
            origin = request.headers.get('Origin')
            allowed = {value.rstrip('/') for value in cors_origins}
            if origin and origin.rstrip('/') not in allowed:
                return {'error': {'code': 'csrf_origin_rejected', 'message': 'Request origin is not allowed.'}}, 403
    
    db_gateway = None
    if not frontend_only:
        # Initialize Flask-Login and register backend blueprints only when
        # backend credentials are intentionally available.
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'

        from backend.db import db
        db_gateway = db

        @login_manager.user_loader
        def load_user(user_id):
            try:
                record = db.get_user(int(user_id))
            except Exception:
                return None
            return FlaskSessionUser(record) if record else None

        from backend.api.analytics import analytics_bp
        from backend.api.admin_content import admin_content_bp
        from backend.api.auth import auth_bp
        from backend.api.courses import courses_bp
        from backend.api.learning import learning_bp
        from backend.api.problems import problems_bp
        from backend.api.submissions import submissions_bp
        from backend.api.teacher import teacher_bp

        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(courses_bp, url_prefix='/api/courses')
        app.register_blueprint(problems_bp, url_prefix='/api/problems')
        app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
        app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
        app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
        app.register_blueprint(admin_content_bp, url_prefix='/api/admin/content')
        app.register_blueprint(learning_bp, url_prefix='/api/learning')
    
    # Multi-page CodeCraft frontend. Each learning surface has a dedicated template.
    @app.context_processor
    def inject_frontend_context():
        return {'backend_enabled': not frontend_only}

    @app.route('/', methods=['GET'])
    def frontend_shell():
        return render_template('pages/home.html', page='home', backend_enabled=not frontend_only)

    @app.route('/<path:page>', methods=['GET'])
    def frontend_page(page):
        allowed = {'home', 'dashboard', 'curriculum', 'course', 'lesson', 'workspace', 'auth', 'profile', 'practice', 'project', 'admin', 'account/login', 'account/register'}
        if page not in allowed:
            return {'error': 'Not found'}, 404
        if page == 'home':
            return render_template('pages/home.html', page='home', backend_enabled=not frontend_only)
        if page == 'course':
            course = COURSE_CATALOG.get(request.args.get('id', 'python'), COURSE_CATALOG['python'])
            return render_template('learning/course.html', page='course', course=course, backend_enabled=not frontend_only)
        if page == 'curriculum':
            total_lesson_count = sum(
                len(module.get('lessons', []))
                for course in COURSE_CATALOG.values()
                for module in course.get('modules', [])
            )
            return render_template(
                'learning/curriculum.html',
                page='curriculum',
                path_nodes=LEARNING_PATH_NODES,
                total_lesson_count=total_lesson_count,
                backend_enabled=not frontend_only,
            )
        if page == 'admin':
            return render_template('admin/content-studio.html', page='admin', backend_enabled=not frontend_only)
        if page == 'account/login':
            return render_template('account/login.html', page='auth', auth_mode='login', backend_enabled=not frontend_only)
        if page == 'account/register':
            return render_template('account/register.html', page='auth', auth_mode='register', backend_enabled=not frontend_only)
        if page == 'auth':
            return render_template('account/login.html', page='auth', auth_mode='login', backend_enabled=not frontend_only)
        if page == 'lesson':
            course = COURSE_CATALOG.get(request.args.get('course', 'python'), COURSE_CATALOG['python'])
            lesson_id = request.args.get('lesson', course['first_lesson'])
            lesson = next((item for module in course['modules'] for item in module['lessons'] if item['id'] == lesson_id), course['modules'][0]['lessons'][0])
            lesson = dict(lesson)
            lesson['unit'] = next((module['title'] for module in course['modules'] if any(item['id'] == lesson['id'] for item in module['lessons'])), 'Module')
            challenge_catalog = load_challenges(db_gateway, PRACTICE_CHALLENGES) if db_gateway else PRACTICE_CHALLENGES
            lesson_challenges = [item for item in challenge_catalog if item['course_id'] == course['id'] and item['lesson_id'] == lesson_id]
            return render_template('learning/lesson.html', page='lesson', course=course, lesson=lesson, lesson_challenges=lesson_challenges, backend_enabled=not frontend_only)
        if page == 'workspace':
            challenge_catalog = load_challenges(db_gateway, PRACTICE_CHALLENGES) if db_gateway else PRACTICE_CHALLENGES
            selected_id = request.args.get('challenge', '')
            selected_challenge = next((item for item in challenge_catalog if item.get('id') == selected_id), None)
            return render_template('learning/workspace.html', page='workspace', course_catalog=COURSE_CATALOG, practice_challenges=challenge_catalog, selected_challenge=selected_challenge, backend_enabled=not frontend_only)
        if page == 'practice':
            course_id = request.args.get('course', 'all')
            difficulty = request.args.get('difficulty', 'all')
            challenge_catalog = load_challenges(db_gateway, PRACTICE_CHALLENGES) if db_gateway else PRACTICE_CHALLENGES
            challenges = [item for item in challenge_catalog if course_id in {'all', item['course_id']} and difficulty in {'all', item['difficulty']}]
            return render_template('learning/practice.html', page='practice', challenges=challenges, projects=PROJECT_CATALOG, selected_course=course_id, selected_difficulty=difficulty, backend_enabled=not frontend_only)
        if page == 'project':
            project = get_project(request.args.get('id', PROJECT_CATALOG[0]['id']))
            if not project:
                return {'error': 'Project not found'}, 404
            return render_template('learning/project.html', page='project', project=project, backend_enabled=not frontend_only)
        return render_template(f'learning/{page}.html' if page in {'dashboard', 'profile'} else f'pages/{page}.html', page=page, backend_enabled=not frontend_only)

    @app.route('/api/public-config', methods=['GET'])
    def public_config():
        return {
            'supabase_url': os.getenv('SUPABASE_URL', ''),
            'supabase_publishable_key': os.getenv('SUPABASE_PUBLISHABLE_KEY', ''),
        }, 200

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'version': '1.0.0'}, 200

    @app.route('/api/ready', methods=['GET'])
    def readiness_check():
        if frontend_only:
            return {'status': 'ready', 'mode': 'frontend-only'}, 200
        required = [
            'SECRET_KEY', 'SUPABASE_URL', 'SUPABASE_PUBLISHABLE_KEY',
            'SUPABASE_SERVICE_ROLE_KEY',
        ]
        queue_mode = os.getenv('SUBMISSION_QUEUE_MODE', 'thread').lower()
        if queue_mode == 'redis':
            required.append('REDIS_URL')
        if os.getenv('SANDBOX_URL'):
            required.append('SANDBOX_TOKEN')
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            return {'status': 'not_ready', 'missing': missing}, 503
        try:
            response = requests.get(
                f"{os.environ['SUPABASE_URL'].rstrip('/')}/rest/v1/",
                headers={
                    'apikey': os.environ['SUPABASE_SERVICE_ROLE_KEY'],
                    'Authorization': f"Bearer {os.environ['SUPABASE_SERVICE_ROLE_KEY']}",
                },
                timeout=2,
            )
            response.raise_for_status()
        except requests.RequestException:
            app.logger.warning('Supabase readiness probe failed', exc_info=True)
            return {'status': 'not_ready', 'dependency': 'supabase'}, 503
        return {'status': 'ready', 'mode': 'backend'}, 200
    
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        response.headers.setdefault('Content-Security-Policy', "default-src 'self'; connect-src 'self' https://*.supabase.co; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self'")
        if request.is_secure:
            response.headers.setdefault('Strict-Transport-Security', 'max-age=31536000; includeSubDomains')
        return response

    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal server error'}, 500
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(
        host=os.getenv('HOST', '127.0.0.1'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    )
