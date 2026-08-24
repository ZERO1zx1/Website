"""CodeCraft email security-code delivery over Gmail SMTP.

This module intentionally does not use Google OAuth or Supabase Auth. Gmail is
only the outbound mail provider; CodeCraft owns the OTP challenge and session.
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import smtplib
import ssl
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.message import EmailMessage
from threading import Lock


class EmailCodeError(RuntimeError):
    """Base error for security-code delivery and verification."""


class EmailDeliveryNotConfigured(EmailCodeError):
    """SMTP credentials are missing."""


class EmailDeliveryFailed(EmailCodeError):
    """The SMTP server rejected or could not receive the message."""


class InvalidEmailCode(EmailCodeError):
    """The challenge, code, or expiry is invalid."""


@dataclass
class _Challenge:
    email: str
    digest: str
    expires_at: datetime
    attempts: int = 0


_challenges: dict[str, _Challenge] = {}
_lock = Lock()


def _clean_email(email: str) -> str:
    return str(email or "").strip().lower()


def _settings() -> tuple[str, int, str, str, str]:
    host = os.getenv("SMTP_HOST", "smtp.gmail.com").strip()
    try:
        port = int(os.getenv("SMTP_PORT", "587"))
    except ValueError as exc:
        raise EmailDeliveryNotConfigured("SMTP_PORT must be an integer") from exc
    username = (os.getenv("SMTP_USER") or os.getenv("GMAIL_USER") or "").strip()
    password = os.getenv("SMTP_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD") or ""
    sender = (os.getenv("SMTP_FROM") or username).strip()
    if not username or not password or not sender:
        raise EmailDeliveryNotConfigured(
            "SMTP_USER and SMTP_PASSWORD (Gmail App Password) are required"
        )
    return host, port, username, password, sender


def _challenge_secret() -> str:
    return os.getenv("SECRET_KEY", "dev-secret-key-change-in-production")


def _digest(challenge: str, email: str, code: str) -> str:
    value = f"{challenge}:{email}:{code}".encode("utf-8")
    return hmac.new(_challenge_secret().encode("utf-8"), value, hashlib.sha256).hexdigest()


def _prune(now: datetime) -> None:
    expired = [key for key, item in _challenges.items() if item.expires_at <= now]
    for key in expired:
        _challenges.pop(key, None)


def _send_message(recipient: str, code: str, expires_minutes: int) -> None:
    host, port, username, password, sender = _settings()
    message = EmailMessage()
    message["Subject"] = "CodeCraft Academy баталгаажуулах код"
    message["From"] = sender
    message["To"] = recipient
    message.set_content(
        "Сайн байна уу,\n\n"
        f"Таны CodeCraft Academy security code: {code}\n\n"
        f"Энэ код {expires_minutes} минутын дараа хүчингүй болно."
        " Кодоо бусдад бүү дамжуулаарай.\n\n"
        "Хэрэв та энэ хүсэлтийг хийгээгүй бол энэ имэйлийг үл тооно уу.\n\n"
        "CodeCraft Academy"
    )
    context = ssl.create_default_context()
    try:
        if port == 465:
            with smtplib.SMTP_SSL(host, port, timeout=15, context=context) as server:
                server.login(username, password)
                server.send_message(message)
        else:
            with smtplib.SMTP(host, port, timeout=15) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(username, password)
                server.send_message(message)
    except (OSError, smtplib.SMTPException) as exc:
        raise EmailDeliveryFailed("SMTP security-code delivery failed") from exc


def issue_email_code(email: str, expires_minutes: int = 10) -> str:
    """Send one code and return an opaque challenge identifier.

    Only a keyed digest is retained in process memory. The plaintext code is
    never logged or returned to the browser. A later successful verification
    consumes the challenge, making it one-time-use for a single-process local
    deployment.
    """
    recipient = _clean_email(email)
    if not recipient:
        raise InvalidEmailCode("Email is required")
    if not 1 <= expires_minutes <= 30:
        raise ValueError("expires_minutes must be between 1 and 30")

    code = f"{secrets.randbelow(1_000_000):06d}"
    challenge = secrets.token_urlsafe(32)
    now = datetime.now(timezone.utc)
    _send_message(recipient, code, expires_minutes)
    with _lock:
        _prune(now)
        _challenges[challenge] = _Challenge(
            email=recipient,
            digest=_digest(challenge, recipient, code),
            expires_at=now + timedelta(minutes=expires_minutes),
        )
    return challenge


def verify_email_code(email: str, challenge: str, code: str) -> None:
    """Verify and consume a code, raising ``InvalidEmailCode`` on failure."""
    recipient = _clean_email(email)
    supplied = str(code or "").strip()
    if not recipient or not challenge or len(supplied) != 6 or not supplied.isdigit():
        raise InvalidEmailCode("Invalid security code")

    now = datetime.now(timezone.utc)
    with _lock:
        _prune(now)
        item = _challenges.get(challenge)
        if not item or item.email != recipient or item.expires_at <= now:
            _challenges.pop(challenge, None)
            raise InvalidEmailCode("Security code is invalid or expired")
        item.attempts += 1
        expected = _digest(challenge, recipient, supplied)
        valid = hmac.compare_digest(item.digest, expected)
        if valid:
            _challenges.pop(challenge, None)
            return
        if item.attempts >= 5:
            _challenges.pop(challenge, None)
        raise InvalidEmailCode("Security code is invalid or expired")
