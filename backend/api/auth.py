"""CodeCraft-owned authentication endpoints for CodeCraft Academy."""

import os
import re
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import requests
from functools import wraps

import jwt
from flask import Blueprint, current_app, make_response, redirect, request, url_for

from backend.db import db
from backend.email_service import (
    EmailDeliveryFailed,
    EmailDeliveryNotConfigured,
    InvalidEmailCode,
    issue_email_code,
    verify_email_code,
)
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


def _secret_key() -> str:
    return current_app.config.get("SECRET_KEY") or os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


def _issue_token(user: dict) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "user_id": int(user["id"]),
            "role": user.get("role", "student"),
            "iat": int(now.timestamp()),
            "exp": int((now + timedelta(days=1)).timestamp()),
        },
        _secret_key(),
        algorithm="HS256",
    )


def _external_auth_payload(auth_response, provider: str = "email") -> dict:
    """Map a Supabase provider response to the app's local JWT contract."""
    auth_user = _auth_value(auth_response, "user")
    if not auth_user:
        raise RuntimeError("Provider response did not include a user")
    auth_user_id = str(_auth_value(auth_user, "id", ""))
    email = _auth_value(auth_user, "email")
    metadata = _auth_value(auth_user, "user_metadata", {}) or {}
    name = metadata.get("display_name") or metadata.get("full_name") or metadata.get("name") or (email.split("@", 1)[0] if email else "суралцагч")
    if not auth_user_id or not email:
        raise RuntimeError("Provider response did not include identity fields")
    user = db.ensure_external_user(
        auth_user_id=auth_user_id,
        email=email,
        name=name,
        provider=provider,
        avatar_url=metadata.get("avatar_url") or metadata.get("picture"),
    )
    if not user:
        raise RuntimeError("Could not create local user projection")
    return {"provider": provider, "token": _issue_token(user), "user": _public_user(user)}


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
                "A valid CodeCraft session token is required.",
                "CodeCraft-ийн хүчинтэй session token шаардлагатай.",
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
                "The CodeCraft session is invalid or has expired.",
                "CodeCraft-ийн session хүчингүй эсвэл хугацаа нь дууссан байна.",
                401,
            )
        return function(current_user, *args, **kwargs)

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
    return f"{_frontend_url().rstrip('/')}/"


def _google_callback_url() -> str:
    return os.getenv(
        "GOOGLE_OAUTH_REDIRECT_URL",
        f"{_frontend_url().rstrip('/')}/api/auth/google/callback",
    ).rstrip("/")


def _google_authorization_url() -> str:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    if not client_id:
        raise RuntimeError("GOOGLE_CLIENT_ID is not configured")
    state = jwt.encode(
        {"nonce": secrets.token_urlsafe(24), "iat": int(datetime.now(timezone.utc).timestamp()), "exp": int((datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp())},
        _secret_key(), algorithm="HS256",
    )
    return "https://accounts.google.com/o/oauth2/v2/auth?" + urlencode({
        "client_id": client_id,
        "redirect_uri": _google_callback_url(),
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "access_type": "online",
        "prompt": "select_account",
    })


def _google_identity(code: str) -> dict:
    client_id = os.getenv("GOOGLE_CLIENT_ID")
    client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        raise RuntimeError("Google OAuth credentials are not configured")
    token_response = requests.post("https://oauth2.googleapis.com/token", data={
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": _google_callback_url(),
        "grant_type": "authorization_code",
    }, timeout=8)
    token_response.raise_for_status()
    id_token = token_response.json().get("id_token")
    if not id_token:
        raise RuntimeError("Google token response did not include id_token")
    identity_response = requests.get("https://oauth2.googleapis.com/tokeninfo", params={"id_token": id_token}, timeout=8)
    identity_response.raise_for_status()
    identity = identity_response.json()
    if identity.get("aud") != client_id or identity.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        raise RuntimeError("Google identity verification failed")
    if identity.get("email_verified") not in {True, "true", "True"}:
        raise RuntimeError("Google email is not verified")
    return identity


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
    """Turn a legacy provider response into the app's stable local-session contract."""
    return _external_auth_payload(auth_response, provider)


def _local_session_payload(user: dict | object) -> dict:
    """Issue an app session from a local user, retaining provider compatibility for older adapters."""
    if isinstance(user, dict) and user.get("id") is not None:
        return {"provider": "password", "token": _issue_token(user), "user": _public_user(user)}
    return _session_payload(user, "password")


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
        user = db.create_user(email=email, password=password, name=name, role="student")
        payload = {"provider": "password", "token": _issue_token(user), "user": _public_user(user)}
        return _session_response({
            "message": "Account created successfully.",
            "message_mn": "Бүртгэл амжилттай үүслээ.",
            **payload,
        }, 201)
    except Exception as exc:
        import sys
        print(f"REGISTER_ERROR: {exc}", file=sys.stderr)
        text = str(exc).lower()
        if "already" in text or "registered" in text or "exists" in text:
            return error_response("email_registered", "This email is already registered.", "Энэ имэйл аль хэдийн бүртгэгдсэн байна.", 409)
        return error_response(
            "registration_failed",
            "The CodeCraft account could not be created.",
            "CodeCraft бүртгэл үүсгэхэд алдаа гарлаа.",
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
        user = db.sign_in_with_password(email, password)
        payload = _local_session_payload(user)
        return _session_response({"message": "Signed in.", "message_mn": "Амжилттай нэвтэрлээ.", **payload}, 200)
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
        challenge = issue_email_code(email)
        return {
            "message": "A one-time code was sent to your email.",
            "message_mn": "Нэг удаагийн security code таны Gmail рүү илгээгдлээ.",
            "email": email,
            "challenge": challenge,
            "expires_in_minutes": 10,
        }, 200
    except EmailDeliveryNotConfigured:
        return error_response(
            "email_delivery_not_configured",
            "Email delivery is not configured.",
            "Gmail SMTP тохиргоо хийгдээгүй байна. .env дотор SMTP_USER, SMTP_PASSWORD тохируулна уу.",
            503,
        )
    except EmailDeliveryFailed:
        return error_response(
            "otp_request_failed",
            "The security code could not be sent.",
            "Security code имэйлээр илгээгдсэнгүй. Gmail App Password болон SMTP тохиргоог шалгана уу.",
            502,
        )
    except Exception:
        return error_response(
            "otp_request_failed",
            "The security code could not be sent.",
            "Security code имэйлээр илгээгдсэнгүй.",
            502,
        )


@auth_bp.route("/otp/verify", methods=["POST"])
def verify_email_otp():
    data = request.get_json(silent=True) or {}
    email = str(data.get("email", "")).strip().lower()
    challenge = str(data.get("challenge", "")).strip()
    code = str(data.get("code", "")).strip()
    if not _valid_email(email) or not challenge or not re.fullmatch(r"\d{6}", code):
        return error_response("invalid_otp", "Enter an email, challenge, and six-digit code.", "Имэйл, challenge болон зургаан оронтой код оруулна уу.", 400)
    try:
        verify_email_code(email, challenge, code)
        user = db.get_user_by_email(email)
        if not user:
            return error_response("user_not_found", "No CodeCraft account exists for this email.", "Энэ имэйлээр CodeCraft бүртгэл олдсонгүй.", 404)
        return _session_response({
            **_local_session_payload(user),
            "message": "Email verification completed.",
            "message_mn": "Gmail security code баталгаажлаа. Амжилттай нэвтэрлээ.",
        })
    except InvalidEmailCode:
        return error_response("otp_verification_failed", "The code is invalid or expired.", "Код буруу эсвэл хугацаа нь дууссан байна.", 401)
    except Exception:
        return error_response("otp_verification_failed", "The email code could not be verified.", "Security code баталгаажуулахад алдаа гарлаа.", 401)


@auth_bp.route("/google/start", methods=["GET"])
def google_start():
    try:
        return {"url": _google_authorization_url()}, 200
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
    state = request.args.get("state", "").strip()
    if not code or not state:
        return redirect(f"{_frontend_url()}?auth_error=google_oauth_failed")
    try:
        jwt.decode(state, _secret_key(), algorithms=["HS256"])
        identity = _google_identity(code)
        user = db.ensure_google_user(
            subject=str(identity["sub"]),
            email=str(identity["email"]),
            display_name=str(identity.get("name") or identity["email"].split("@", 1)[0]),
            avatar_url=identity.get("picture"),
        )
        payload = {"provider": "google", "token": _issue_token(user), "user": _public_user(user)}
        response = redirect(f"{_frontend_url()}?auth_provider=google")
        response.set_cookie("codecraft_session", payload["token"], max_age=86400, httponly=True,
                            secure=current_app.config.get("ENVIRONMENT") == "production",
                            samesite="Lax", path="/")
        return response
    except Exception:
        return redirect(f"{_frontend_url()}?auth_error=google_oauth_failed")


@auth_bp.route("/logout", methods=["POST"])
def logout():
    response = make_response({"message": "Signed out."}, 200)
    response.delete_cookie("codecraft_session", path="/", samesite="Lax")
    return response


@auth_bp.route("/me", methods=["GET"])
@token_required
def get_current_user(current_user):
    return {"user": _public_user(current_user)}, 200


@auth_bp.route("/users/<int:user_id>/role", methods=["PATCH"])
@token_required
def update_user_role(current_user, user_id):
    if current_user.get("role") not in {"owner", "admin"}:
        return error_response(
            "permission_denied",
            "Only an owner or admin can change roles.",
            "Зөвхөн owner эсвэл admin хэрэглэгч үүрэг өөрчилж болно.",
            403,
        )
    data = request.get_json(silent=True) or {}
    role = str(data.get("role", "")).strip().lower()
    if role not in {"student", "teacher", "admin", "owner"}:
        return error_response(
            "invalid_role",
            "The requested role is invalid.",
            "Хүссэн үүрэг буруу байна.",
            400,
        )
    try:
        user = db.update_user(user_id, {"role": role})
    except Exception:
        return error_response("role_update_failed", "The user role could not be updated.", "Хэрэглэгчийн үүрэг шинэчлэгдсэнгүй.", 502)
    if not user:
        return error_response("user_not_found", "The user was not found.", "Хэрэглэгч олдсонгүй.", 404)
    return {"user": _public_user(user), "message_mn": "Хэрэглэгчийн үүрэг шинэчлэгдлээ."}, 200
