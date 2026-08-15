"""Programming Learning Intelligence Platform Flask application factory."""

import logging
import os
from urllib.parse import urlparse

import requests
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template, request
from flask_cors import CORS
from flask_login import LoginManager


logger = logging.getLogger(__name__)
load_dotenv()


class FlaskSessionUser:
    """Minimal Flask-Login user wrapper for the JWT-backed database record."""

    def __init__(self, record):
        self.record = record
        self.id = record.get("id")
        self.name = record.get("name")
        self.email = record.get("email")
        self.role = record.get("role", "student")

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


def _is_true(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _valid_http_url(value: str | None) -> bool:
    if not value:
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def _required_config_missing(frontend_only: bool) -> list[str]:
    if frontend_only:
        return []
    development = os.getenv("FLASK_ENV", "development").lower() != "production"
    local_setting = os.getenv("LOCAL_DB")
    local_db = development and (_is_true(local_setting) or (local_setting is None and (not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY"))))
    required = ["SECRET_KEY"] if local_db else ["SECRET_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    if os.getenv("SUBMISSION_QUEUE_MODE", "thread").lower() == "redis":
        required.append("REDIS_URL")
    if os.getenv("SANDBOX_URL"):
        required.append("SANDBOX_TOKEN")
    missing = [name for name in required if not os.getenv(name, "").strip()]
    if os.getenv("SUPABASE_URL") and not _valid_http_url(os.getenv("SUPABASE_URL")):
        missing.append("SUPABASE_URL(valid URL)")
    return missing


def _production_missing_config(environment: str, frontend_only: bool) -> list[str]:
    if environment != "production":
        return []
    return _required_config_missing(frontend_only)


def create_app(config_name="development"):
    """Create and configure the Flask application."""
    app = Flask(__name__, template_folder="frontend/templates", static_folder="frontend/static")

    environment = os.getenv("FLASK_ENV", config_name or "development").lower()
    frontend_only = _is_true(os.getenv("FRONTEND_ONLY", "false"))
    missing_production = _production_missing_config(environment, frontend_only)
    if missing_production:
        raise RuntimeError("Missing required production configuration: " + ", ".join(missing_production))

    secret_key = os.getenv("SECRET_KEY")
    app.config.update(
        ENVIRONMENT=environment,
        SECRET_KEY=secret_key or "dev-secret-key-change-in-production",
        JSON_SORT_KEYS=False,
        JSONIFY_PRETTYPRINT_REGULAR=True,
        MAX_CONTENT_LENGTH=int(os.getenv("MAX_CONTENT_LENGTH", str(256 * 1024))),
        FRONTEND_ONLY=frontend_only,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=environment == "production",
        SESSION_COOKIE_SAMESITE="Lax",
    )

    cors_origins = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", "http://localhost:5000,http://127.0.0.1:5000").split(",")
        if origin.strip()
    ]
    app.config["CORS_ORIGINS"] = cors_origins
    CORS(
        app,
        resources={
            r"/api/*": {
                "origins": cors_origins,
                "methods": ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
                "allow_headers": ["Content-Type", "Authorization", "Accept-Language"],
                "supports_credentials": True,
            }
        },
    )

    if not frontend_only:
        login_manager = LoginManager()
        login_manager.init_app(app)
        login_manager.login_view = "auth.login"
        app.login_manager = login_manager

        from backend.db import db

        @login_manager.user_loader
        def load_user(user_id):
            try:
                record = db.get_user(int(user_id))
            except Exception:
                logger.exception("Unable to load authenticated user")
                return None
            return FlaskSessionUser(record) if record else None

        from backend.api.analytics import analytics_bp
        from backend.api.auth import auth_bp
        from backend.api.exams import exams_bp
        from backend.api.courses import courses_bp
        from backend.api.problems import problems_bp
        from backend.api.submissions import submissions_bp
        from backend.api.teacher import teacher_bp

        app.register_blueprint(auth_bp, url_prefix="/api/auth")
        app.register_blueprint(courses_bp, url_prefix="/api/courses")
        app.register_blueprint(problems_bp, url_prefix="/api/problems")
        app.register_blueprint(submissions_bp, url_prefix="/api/submissions")
        app.register_blueprint(teacher_bp, url_prefix="/api/teacher")
        app.register_blueprint(analytics_bp, url_prefix="/api/analytics")
        app.register_blueprint(exams_bp, url_prefix="/api/exams")

    @app.route("/", methods=["GET"])
    def frontend_shell():
        return render_template("index.html", backend_enabled=not frontend_only)

    @app.route("/home", methods=["GET"])
    def home_page():
        return render_template("pages/home.html", backend_enabled=not frontend_only, page_class="home-page")

    @app.route("/login", methods=["GET"])
    def login_page():
        return render_template("pages/login.html", backend_enabled=not frontend_only, page_class="login-page")

    @app.route("/register", methods=["GET"])
    def register_page():
        return render_template("pages/register.html", backend_enabled=not frontend_only, page_class="register-page")

    @app.route("/password-reset", methods=["GET"])
    def password_reset_page():
        return render_template("pages/password_reset.html", backend_enabled=not frontend_only, page_class="password-reset-page")

    @app.route("/dashboard", methods=["GET"])
    def dashboard_page():
        return render_template(
            "pages/workspace_dashboard.html",
            backend_enabled=not frontend_only,
            page_class="workspace-dashboard-page",
            workspace_page="dashboard",
            breadcrumb="Dashboard",
        )

    @app.route("/learn", methods=["GET"])
    @app.route("/courses", methods=["GET"])
    def learn_page():
        return render_template(
            "pages/learn.html",
            backend_enabled=not frontend_only,
            page_class="workspace-learn-page",
            workspace_page="learn",
            breadcrumb="Learning paths",
        )

    @app.route("/practice", methods=["GET"])
    def practice_page():
        return render_template(
            "pages/practice.html",
            backend_enabled=not frontend_only,
            page_class="workspace-practice-page",
            workspace_page="practice",
            breadcrumb="Practice library",
        )

    @app.route("/assessments", methods=["GET"])
    @app.route("/exams", methods=["GET"])
    def assessments_page():
        return render_template(
            "pages/assessments.html",
            backend_enabled=not frontend_only,
            page_class="workspace-assessments-page",
            workspace_page="assessments",
            breadcrumb="Assessments",
        )

    @app.route("/profile", methods=["GET"])
    def profile_page():
        return render_template(
            "pages/profile.html",
            backend_enabled=not frontend_only,
            page_class="workspace-profile-page",
            workspace_page="profile",
            breadcrumb="Profile",
        )

    @app.route("/settings", methods=["GET"])
    def settings_page():
        return render_template(
            "pages/settings.html",
            backend_enabled=not frontend_only,
            page_class="workspace-settings-page",
            workspace_page="settings",
            breadcrumb="Preferences",
        )

    @app.route("/api/health", methods=["GET"])
    def health_check():
        return {"status": "healthy", "version": "1.0.0", "mode": "frontend-only" if frontend_only else "backend"}, 200

    @app.route("/api/ready", methods=["GET"])
    def readiness_check():
        if frontend_only:
            return {"status": "ready", "mode": "frontend-only", "checks": {}}, 200

        missing = _required_config_missing(frontend_only)
        if missing:
            return {"status": "not_ready", "missing": missing, "checks": {}}, 503

        checks = {"configuration": "ok"}
        if not _is_true(os.getenv("READINESS_PROBE", "true")):
            return {"status": "ready", "mode": "backend", "checks": checks, "probes_skipped": True}, 200

        local_setting = os.getenv("LOCAL_DB")
        if environment != "production" and (_is_true(local_setting) or (local_setting is None and (not os.getenv("SUPABASE_URL") or not os.getenv("SUPABASE_KEY")))):
            checks["database"] = "local_sqlite"
        else:
            supabase_url = os.getenv("SUPABASE_URL", "").rstrip("/")
            try:
                response = requests.get(
                    f"{supabase_url}/rest/v1/users?select=id&limit=1",
                    headers={"apikey": os.getenv("SUPABASE_KEY", ""), "Authorization": f"Bearer {os.getenv('SUPABASE_KEY', '')}"},
                    timeout=2,
                )
                if response.status_code >= 400:
                    checks["supabase"] = f"unavailable:{response.status_code}"
                else:
                    checks["supabase"] = "ok"
            except requests.RequestException:
                checks["supabase"] = "unavailable"

        redis_url = os.getenv("REDIS_URL")
        if os.getenv("SUBMISSION_QUEUE_MODE", "thread").lower() == "redis":
            try:
                import redis

                redis.from_url(redis_url, socket_connect_timeout=2, socket_timeout=2).ping()
                checks["redis"] = "ok"
            except Exception:
                checks["redis"] = "unavailable"

        sandbox_url = os.getenv("SANDBOX_URL")
        if sandbox_url:
            try:
                response = requests.get(f"{sandbox_url.rstrip('/')}/health", timeout=2)
                checks["sandbox"] = "ok" if response.ok else f"unavailable:{response.status_code}"
            except requests.RequestException:
                checks["sandbox"] = "unavailable"

        unavailable = [name for name, status in checks.items() if status not in {"ok", "local_sqlite"}]
        if unavailable:
            return {"status": "not_ready", "mode": "backend", "checks": checks}, 503
        return {"status": "ready", "mode": "backend", "checks": checks}, 200

    @app.after_request
    def add_security_headers(response):
        response.headers.setdefault("X-Content-Type-Options", "nosniff")
        response.headers.setdefault("X-Frame-Options", "SAMEORIGIN")
        response.headers.setdefault("Referrer-Policy", "strict-origin-when-cross-origin")
        response.headers.setdefault("Permissions-Policy", "camera=(), microphone=(), geolocation=()")
        response.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; connect-src 'self' https://*.supabase.co; font-src 'self' https://fonts.gstatic.com; img-src 'self' data:; script-src 'self'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; worker-src 'self' blob:; frame-ancestors 'self'; base-uri 'self'; form-action 'self'",
        )
        if request.is_secure:
            response.headers.setdefault("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        return response

    @app.errorhandler(413)
    def request_too_large(error):
        return jsonify({"error": {"code": "PAYLOAD_TOO_LARGE", "message": "Request payload is too large."}}), 413

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": {"code": "NOT_FOUND", "message": "Resource not found."}}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.exception("Unhandled application error")
        return jsonify({"error": {"code": "INTERNAL_ERROR", "message": "Internal server error."}}), 500

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "5000")),
        debug=_is_true(os.getenv("FLASK_DEBUG", "false")),
    )
