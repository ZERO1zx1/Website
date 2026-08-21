"""Supabase Auth endpoints for CodeCraft Academy."""

import os
import re
from datetime import datetime, timedelta, timezone
from functools import wraps

import jwt
from flask import Blueprint, current_app, make_response, redirect, request, url_for

from backend.db import db
from backend.rbac import error_response

auth_bp = Blueprint("auth", __name__)


def _valid_email(value: str) -> bool:
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", value or ""))


def _auth_value(record, key, default=None):
    if isinstance(record, dict):
        return record.get(key, default)
    return getattr(record, key, default)


def _public_user(profile: dict) -> dict:
    """Limit API output to safe profile fields."""
    return {
        "id": str(profile.get("id", "")),
        "email": profile.get("email"),
        "name": profile.get("name") or profile.get("display_name"),
        "role": profile.get("role", "student"),
        "locale": profile.get("locale", "mn"),
        "theme": profile.get("theme", "system"),
    }


def token_required(function):
    """Validate a Supabase access token and attach its own CodeCraft profile."""
    @wraps(function)
    def decorated(*args, **kwargs):
        header = request.headers.get("Authorization", "")
        parts = header.split()
        token = parts[1] if len(parts) == 2 and parts[0].lower() == "bearer" else request.cookies.get("codecraft_session")
        if not token:
            return error_response(
                "missing_token",
                "A valid Supabase access token is required.",
                "Supabase нэвтрэлтийн хүчинтэй token шаардлагатай.",
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
                "The Supabase session is invalid or has expired.",
                "Supabase нэвтрэлтийн session хүчингүй эсвэл хугацаа нь дууссан байна.",
                401,
            )
        return function(profile, *args, **kwargs)

    return decorated


def role_required(required_role: str):
    """Require a role stored in the learner's Supabase-backed profile."""
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


def _frontend_url() -> str:
    return os.getenv("FRONTEND_URL", request.host_url.rstrip("/"))


def _email_confirmation_url() -> str:
    return f"{_frontend_url().rstrip('/')}/auth?confirmed=1"


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


def _session_payload(auth_response, provider: str = "password") -> dict:
    """Turn a Supabase Auth response into the safe frontend session shape."""
    auth_user = _auth_value(auth_response, "user")
    session = _auth_value(auth_response, "session")
    if not auth_user:
        raise RuntimeError("Supabase Auth did not return a user")
    access_token = _auth_value(session, "access_token") if session else None
    refresh_token = _auth_value(session, "refresh_token") if session else None
    if access_token:
        profile = db.ensure_profile(auth_user, access_token)
    else:
        metadata = _auth_value(auth_user, "user_metadata", {}) or {}
        email = _auth_value(auth_user, "email")
        profile = {
            "id": str(_auth_value(auth_user, "id", "")),
            "email": email,
            "name": metadata.get("display_name") or metadata.get("full_name") or (email.split("@", 1)[0] if email else "суралцагч"),
            "role": "student",
            "locale": "mn",
            "theme": "system",
        }
    payload = {
        "provider": provider,
        "user": _public_user(profile),
    }
    if access_token:
        payload["token"] = access_token
    if refresh_token:
        payload["refresh_token"] = refresh_token
    return payload


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    name = str(data.get("name", "")).strip()
    if not _valid_email(email) or not name or not password:
        return error_response(
            "missing_fields",
            "Name, a valid email, and password are required.",
            "Нэр, хүчинтэй имэйл болон нууц үг заавал шаардлагатай.",
            400,
        )
    if len(password) < 8:
        return error_response(
            "weak_password",
            "Password must contain at least 8 characters.",
            "Нууц үг хамгийн багадаа 8 тэмдэгттэй байна.",
            400,
        )
    try:
        response = db.sign_up_with_password(email, password, name, _email_confirmation_url())
        payload = _session_payload(response, "password")
        if not payload.get("token"):
            return {
                "message": "Check your email to confirm your CodeCraft account.",
                "message_mn": "Имэйлээ шалгаад CodeCraft бүртгэлээ баталгаажуулна уу.",
                "verification_required": True,
                "user": payload["user"],
            }, 202
        return {
            "message": "Account created successfully.",
            "message_mn": "Бүртгэл амжилттай үүслээ.",
            **payload,
        }, 201
    except Exception as exc:
        import sys
        print(f"REGISTER_ERROR: {exc}", file=sys.stderr)
        text = str(exc).lower()
        if "already" in text or "registered" in text or "exists" in text:
            return error_response("email_registered", "This email is already registered.", "Энэ имэйл аль хэдийн бүртгэгдсэн байна.", 409)
        return error_response(
            "registration_failed",
            "The Supabase account could not be created.",
            "Supabase бүртгэл үүсгэхэд алдаа гарлаа.",
            502,
        )


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    password = str(data.get("password", ""))
    if not _valid_email(email) or not password:
        return error_response(
            "missing_credentials",
            "A valid email and password are required.",
            "Хүчинтэй имэйл болон нууц үг заавал шаардлагатай.",
            400,
        )
    try:
        payload = _session_payload(db.sign_in_with_password(email, password), "password")
        return {"message": "Signed in.", "message_mn": "Амжилттай нэвтэрлээ.", **payload}, 200
    except Exception:
        return error_response(
            "invalid_credentials",
            "Invalid credentials or the email has not been confirmed.",
            "Имэйл, нууц үг буруу эсвэл имэйл баталгаажаагүй байна.",
            401,
        )


@auth_bp.route("/otp/request", methods=["POST"])
def request_email_otp():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    if not _valid_email(email):
        return error_response("invalid_email", "Enter a valid email address.", "Хүчинтэй имэйл хаяг оруулна уу.", 400)
    try:
        db.request_email_otp(email, redirect_to=_email_confirmation_url())
        return {
            "message": "A one-time code was sent to your email.",
            "message_mn": "Нэг удаагийн кодыг таны имэйл рүү илгээлээ.",
            "email": email,
        }, 200
    except Exception:
        return error_response(
            "otp_request_failed",
            "The email code could not be sent. Check Supabase email settings.",
            "Имэйлийн код илгээгдсэнгүй. Supabase-ийн email тохиргоог шалгана уу.",
            502,
        )


@auth_bp.route("/otp/verify", methods=["POST"])
def verify_email_otp():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    code = str(data.get("code", "")).strip()
    if not _valid_email(email) or not re.fullmatch(r"\d{6}", code):
        return error_response("invalid_otp", "Enter an email and six-digit code.", "Имэйл болон зургаан оронтой код оруулна уу.", 400)
    try:
        auth_response = db.verify_email_otp(email, code)
        return _session_response(_external_auth_payload(auth_response, "email") | {
            "message": "Email verification completed.",
            "message_mn": "Имэйл баталгаажуулалт амжилттай боллоо.",
        })
    except Exception:
        return error_response("otp_verification_failed", "The code is invalid or expired.", "Код буруу эсвэл хугацаа нь дууссан байна.", 401)


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


@auth_bp.route("/logout", methods=["POST"])
def logout():
    """The browser clears its local tokens; server-side sessions remain stateless."""
    return {"message": "Signed out.", "message_mn": "Амжилттай гарлаа."}, 200
