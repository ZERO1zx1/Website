"""Authentication, session and role-management API routes."""

import os
import re
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Blueprint, current_app, make_response, redirect, request, url_for

from backend.db import db
from backend.rbac import error_response, permission_required

auth_bp = Blueprint("auth", __name__)


def _secret_key() -> str:
    configured = current_app.config.get("SECRET_KEY") if current_app else None
    secret = configured or os.getenv("SECRET_KEY")
    if not secret and os.getenv("FLASK_ENV", "development") == "production":
        raise RuntimeError("SECRET_KEY must be configured in production")
    return secret or "dev-secret"


def token_required(function):
    """Require a valid Bearer JWT and load the current user server-side."""
    @wraps(function)
    def decorated(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        parts = header.split()
        token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else request.cookies.get("codecraft_session")
        if not token:
            return error_response(
                "missing_token",
                "A valid Bearer token is required.",
                "Зөв Bearer token шаардлагатай.",
                401,
            )
        try:
            payload = jwt.decode(token, _secret_key(), algorithms=["HS256"])
            current_user = db.get_user(payload["user_id"])
            if not current_user:
                return error_response(
                    "user_not_found",
                    "The authenticated user was not found.",
                    "Нэвтэрсэн хэрэглэгч олдсонгүй.",
                    401,
                )
        except jwt.ExpiredSignatureError:
            return error_response(
                "token_expired",
                "The authentication token has expired.",
                "Нэвтрэлтийн token-ийн хугацаа дууссан байна.",
                401,
            )
        except (jwt.InvalidTokenError, KeyError, RuntimeError):
            return error_response(
                "invalid_token",
                "The authentication token is invalid.",
                "Нэвтрэлтийн token буруу байна.",
                401,
            )
        return function(current_user, *args, **kwargs)

    return decorated


def role_required(required_role):
    """Backward-compatible exact-role decorator."""
    def decorator(function):
        @wraps(function)
        @token_required
        def decorated(current_user, *args, **kwargs):
            if current_user.get("role") not in {required_role, "owner"}:
                return error_response(
                    "permission_denied",
                    f"This action requires the {required_role} role.",
                    "Танд энэ үйлдлийг хийх зөвшөөрөл байхгүй байна.",
                    403,
                )
            return function(current_user, *args, **kwargs)
        return decorated
    return decorator


def admin_required(function):
    return role_required("admin")(function)


def teacher_required(function):
    return role_required("teacher")(function)


def student_required(function):
    return role_required("student")(function)


def owner_required(function):
    return role_required("owner")(function)


def _public_user(user: dict) -> dict:
    return {
        "id": user.get("id"),
        "email": user.get("email"),
        "name": user.get("name"),
        "role": user.get("role", "student"),
        "requested_role": user.get("requested_role"),
        "teacher_approval_status": user.get("teacher_approval_status"),
    }


def _issue_token(user: dict) -> str:
    return jwt.encode(
        {
            "user_id": user["id"],
            "email": user["email"],
            "role": user.get("role", "student"),
            "exp": datetime.now(timezone.utc) + timedelta(hours=24),
        },
        _secret_key(),
        algorithm="HS256",
    )


def _session_response(payload: dict, status: int = 200):
    response = make_response(payload, status)
    token = payload.get("token")
    if token:
        response.set_cookie(
            "codecraft_session",
            token,
            max_age=24 * 60 * 60,
            httponly=True,
            secure=current_app.config.get("ENVIRONMENT") == "production",
            samesite="Lax",
            path="/",
        )
    return response


def _auth_user_value(auth_user, key, default=None):
    if isinstance(auth_user, dict):
        return auth_user.get(key, default)
    return getattr(auth_user, key, default)


def _external_auth_payload(auth_response, provider: str):
    auth_user = getattr(auth_response, "user", None)
    if not auth_user:
        raise RuntimeError("Supabase Auth did not return a user")
    email = _auth_user_value(auth_user, "email")
    if not email:
        raise RuntimeError("The identity did not include an email address")
    metadata = _auth_user_value(auth_user, "user_metadata", {}) or {}
    name = metadata.get("full_name") or metadata.get("name") or email.split("@", 1)[0]
    avatar_url = metadata.get("avatar_url") or metadata.get("picture")
    local_user = db.ensure_external_user(
        auth_user_id=str(_auth_user_value(auth_user, "id")),
        email=email.strip().lower(),
        name=name,
        provider=provider,
        avatar_url=avatar_url,
    )
    if not local_user:
        raise RuntimeError("The local role record could not be created")
    return {"token": _issue_token(local_user), "user": _public_user(local_user)}


def _frontend_url():
    return os.getenv("FRONTEND_URL", request.host_url.rstrip("/"))


def _google_callback_url():
    return os.getenv("GOOGLE_OAUTH_REDIRECT_URL") or url_for("auth.google_callback", _external=True)


@auth_bp.route("/otp/request", methods=["POST"])
def request_email_otp():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email):
        return error_response(
            "invalid_email",
            "Enter a valid Gmail or email address.",
            "Зөв Gmail эсвэл имэйл хаяг оруулна уу.",
            400,
        )
    try:
        otp_redirect = os.getenv("OTP_REDIRECT_URL") or f"{_frontend_url().rstrip('/')}/"
        db.request_email_otp(email, redirect_to=otp_redirect)
        return {
            "message": "A one-time code was sent to your email.",
            "message_mn": "Нэг удаагийн нэвтрэх кодыг таны имэйл рүү илгээлээ.",
            "email": email,
        }, 200
    except Exception:
        return error_response(
            "otp_request_failed",
            "The email code could not be sent. Check the Supabase email provider configuration.",
            "Имэйлийн код илгээгдсэнгүй. Supabase-ийн email provider тохиргоог шалгана уу.",
            502,
        )


@auth_bp.route("/otp/verify", methods=["POST"])
def verify_email_otp():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    code = str(data.get("code", "")).strip()
    if not email or not re.fullmatch(r"\d{6}", code):
        return error_response(
            "invalid_otp",
            "Enter the email address and six-digit code.",
            "Имэйл хаяг болон зургаан оронтой кодоо оруулна уу.",
            400,
        )
    try:
        auth_response = db.verify_email_otp(email, code)
        return _session_response(_external_auth_payload(auth_response, "email") | {
            "message": "Email verification completed.",
            "message_mn": "Имэйл баталгаажуулалт амжилттай боллоо.",
        })
    except Exception:
        return error_response(
            "otp_verification_failed",
            "The code is invalid or has expired.",
            "Код буруу эсвэл хугацаа нь дууссан байна.",
            401,
        )


@auth_bp.route("/google/start", methods=["GET"])
def google_start():
    try:
        return {"url": db.google_login_url(_google_callback_url())}, 200
    except Exception:
        return error_response(
            "google_oauth_unavailable",
            "Google sign-in is not configured yet.",
            "Google-ээр нэвтрэх тохиргоо одоогоор хийгдээгүй байна.",
            503,
        )


@auth_bp.route("/google/callback", methods=["GET"])
def google_callback():
    code = request.args.get("code", "").strip()
    if not code:
        return redirect(f"{_frontend_url()}?auth_error=google_oauth_failed")
    try:
        auth_response = db.exchange_google_code(code)
        payload = _external_auth_payload(auth_response, "google")
        response = redirect(f"{_frontend_url()}?auth_provider=google")
        response.set_cookie("codecraft_session", payload["token"], max_age=86400, httponly=True,
                            secure=current_app.config.get("ENVIRONMENT") == "production",
                            samesite="Lax", path="/")
        return response
    except Exception:
        return redirect(f"{_frontend_url()}?auth_error=google_oauth_failed")


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    if not data.get("email") or not data.get("password") or not data.get("name"):
        return error_response(
            "missing_fields",
            "Email, password and name are required.",
            "Имэйл, нууц үг болон нэр заавал шаардлагатай.",
            400,
        )
    if len(data["password"]) < 8:
        return error_response(
            "weak_password",
            "Password must contain at least 8 characters.",
            "Нууц үг хамгийн багадаа 8 тэмдэгттэй байна.",
            400,
        )
    if db.get_user_by_email(data["email"].strip().lower()):
        return error_response(
            "email_registered",
            "This email is already registered.",
            "Энэ имэйл аль хэдийн бүртгэгдсэн байна.",
            409,
        )
    try:
        user = db.create_user(
            email=data["email"].strip().lower(),
            password=data["password"],
            name=data["name"].strip(),
            role="student",
        )
        return _session_response({
            "message": "User registered successfully.",
            "message_mn": "Хэрэглэгч амжилттай бүртгэгдлээ.",
            "token": _issue_token(user),
            "user": _public_user(user),
        }, 201)
    except Exception:
        return error_response(
            "registration_failed",
            "The account could not be created.",
            "Бүртгэл үүсгэхэд алдаа гарлаа.",
            500,
        )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    if not data.get("email") or not data.get("password"):
        return error_response(
            "missing_credentials",
            "Email and password are required.",
            "Имэйл болон нууц үг заавал шаардлагатай.",
            400,
        )
    try:
        auth_response = db.sign_in_with_password(
            data["email"].strip().lower(), data["password"]
        )
        payload = _external_auth_payload(auth_response, "email")
    except Exception:
        return error_response(
            "invalid_credentials",
            "Invalid email or password.",
            "Имэйл эсвэл нууц үг буруу байна.",
            401,
        )
    return _session_response(payload)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = make_response({"message": "Signed out."}, 200)
    response.delete_cookie("codecraft_session", path="/", samesite="Lax")
    return response


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    return {"user": _public_user(current_user)}, 200


@auth_bp.route("/request-teacher-role", methods=["POST"])
@token_required
def request_teacher_role(current_user):
    if current_user.get("role") != "student":
        return error_response(
            "role_request_not_allowed",
            "Only students can request teacher approval.",
            "Зөвхөн суралцагч багшийн эрх хүсэх боломжтой.",
            400,
        )
    try:
        db.update_user(current_user["id"], {
            "requested_role": "teacher",
            "teacher_approval_status": "pending",
        })
        return {"message": "Teacher approval request submitted.", "message_mn": "Багшийн эрхийн хүсэлт илгээгдлээ."}, 200
    except Exception:
        return error_response(
            "role_request_failed",
            "The teacher approval request could not be submitted.",
            "Багшийн эрхийн хүсэлт илгээхэд алдаа гарлаа.",
            500,
        )


@auth_bp.route("/approve-teacher/<int:user_id>", methods=["POST"])
@token_required
@permission_required("teachers.approve")
def approve_teacher(current_user, user_id):
    user = db.get_user(user_id)
    if not user:
        return error_response("user_not_found", "User not found.", "Хэрэглэгч олдсонгүй.", 404)
    if user.get("requested_role") != "teacher" or user.get("teacher_approval_status") != "pending":
        return error_response("approval_not_pending", "This teacher request is not pending.", "Энэ багшийн хүсэлт хүлээгдэж байгаа төлөвт биш байна.", 400)
    db.update_user(user_id, {"role": "teacher", "requested_role": None, "teacher_approval_status": "approved"})
    return {"message": "Teacher request approved.", "message_mn": "Багшийн эрхийн хүсэлт баталгаажлаа."}, 200


@auth_bp.route("/reject-teacher/<int:user_id>", methods=["POST"])
@token_required
@permission_required("teachers.approve")
def reject_teacher(current_user, user_id):
    user = db.get_user(user_id)
    if not user:
        return error_response("user_not_found", "User not found.", "Хэрэглэгч олдсонгүй.", 404)
    if user.get("requested_role") != "teacher" or user.get("teacher_approval_status") != "pending":
        return error_response("approval_not_pending", "This teacher request is not pending.", "Энэ багшийн хүсэлт хүлээгдэж байгаа төлөвт биш байна.", 400)
    db.update_user(user_id, {"role": "student", "requested_role": None, "teacher_approval_status": "rejected"})
    return {"message": "Teacher request rejected.", "message_mn": "Багшийн эрхийн хүсэлт татгалзагдлаа."}, 200


@auth_bp.route("/pending-teachers", methods=["GET"])
@token_required
@permission_required("teachers.approve")
def get_pending_teachers(current_user):
    return {"pending_teachers": db.get_pending_teacher_requests()}, 200


@auth_bp.route("/users/<int:user_id>/role", methods=["PATCH"])
@owner_required
def update_user_role(current_user, user_id):
    data = request.get_json(silent=True) or {}
    new_role = data.get("role")
    if new_role not in {"owner", "admin", "teacher", "student"}:
        return error_response("invalid_role", "The requested role is invalid.", "Хүссэн үүрэг буруу байна.", 400)
    user = db.get_user(user_id)
    if not user:
        return error_response("user_not_found", "User not found.", "Хэрэглэгч олдсонгүй.", 404)
    db.update_user(user_id, {"role": new_role, "requested_role": None, "teacher_approval_status": "approved"})
    return {"message": "User role updated.", "message_mn": "Хэрэглэгчийн үүрэг шинэчлэгдлээ.", "user_id": user_id, "role": new_role}, 200
