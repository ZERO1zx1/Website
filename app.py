"""
Programming Learning Intelligence Platform
Flask Application Factory
"""

import os
from flask import Flask, render_template, request
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv


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
    
    if not frontend_only:
        # Initialize Flask-Login and register backend blueprints only when
        # backend credentials are intentionally available.
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'

        from backend.db import db

        @login_manager.user_loader
        def load_user(user_id):
            try:
                record = db.get_user(int(user_id))
            except Exception:
                return None
            return FlaskSessionUser(record) if record else None

        from backend.api.auth import auth_bp
        from backend.api.courses import courses_bp
        from backend.api.problems import problems_bp
        from backend.api.submissions import submissions_bp
        from backend.api.teacher import teacher_bp
        from backend.api.analytics import analytics_bp

        app.register_blueprint(auth_bp, url_prefix='/api/auth')
        app.register_blueprint(courses_bp, url_prefix='/api/courses')
        app.register_blueprint(problems_bp, url_prefix='/api/problems')
        app.register_blueprint(submissions_bp, url_prefix='/api/submissions')
        app.register_blueprint(teacher_bp, url_prefix='/api/teacher')
        app.register_blueprint(analytics_bp, url_prefix='/api/analytics')
    
    # Frontend shell. Data loading is performed by the browser adapter so the
    # same shell can run in demo mode or with authenticated backend APIs.
    @app.route('/', methods=['GET'])
    def frontend_shell():
        return render_template('index.html', backend_enabled=not frontend_only)

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'version': '1.0.0'}, 200

    @app.route('/api/ready', methods=['GET'])
    def readiness_check():
        if frontend_only:
            return {'status': 'ready', 'mode': 'frontend-only'}, 200
        required = ['SECRET_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
        queue_mode = os.getenv('SUBMISSION_QUEUE_MODE', 'thread').lower()
        if queue_mode == 'redis':
            required.append('REDIS_URL')
        if os.getenv('SANDBOX_URL'):
            required.append('SANDBOX_TOKEN')
        missing = [name for name in required if not os.getenv(name)]
        if missing:
            return {'status': 'not_ready', 'missing': missing}, 503
        return {'status': 'ready', 'mode': 'backend'}, 200
    
    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault('X-Content-Type-Options', 'nosniff')
        response.headers.setdefault('X-Frame-Options', 'SAMEORIGIN')
        response.headers.setdefault('Referrer-Policy', 'strict-origin-when-cross-origin')
        response.headers.setdefault('Permissions-Policy', 'camera=(), microphone=(), geolocation=()')
        response.headers.setdefault('Content-Security-Policy', "default-src 'self'; connect-src 'self' https://*.supabase.co; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; frame-ancestors 'self'; base-uri 'self'; form-action 'self'")
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
        host=os.getenv('HOST', '0.0.0.0'),
        port=int(os.getenv('PORT', 5000)),
        debug=os.getenv('FLASK_DEBUG', 'false').lower() == 'true'
    )
