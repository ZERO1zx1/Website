"""
Programming Learning Intelligence Platform
Flask Application Factory
"""

import os
from flask import Flask, render_template
from flask_cors import CORS
from flask_login import LoginManager
from dotenv import load_dotenv

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
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JSON_SORT_KEYS'] = False
    app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
    frontend_only = os.getenv('FRONTEND_ONLY', 'false').lower() == 'true'
    app.config['FRONTEND_ONLY'] = frontend_only
    
    # CORS Configuration
    CORS(app, resources={
        r"/api/*": {
            "origins": ["*"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    if not frontend_only:
        # Initialize Flask-Login and register backend blueprints only when
        # backend credentials are intentionally available.
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = 'auth.login'

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
    
    # Frontend shell. It intentionally renders without calling backend data APIs;
    # the browser adapter uses mock data until the integration phase.
    @app.route('/', methods=['GET'])
    def frontend_shell():
        return render_template('index.html', backend_enabled=not frontend_only)

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy', 'version': '1.0.0'}, 200
    
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
        debug=os.getenv('FLASK_DEBUG', False)
    )
