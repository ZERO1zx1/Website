"""Role and permission helpers loaded from config/roles.yml."""

from functools import wraps
from pathlib import Path
from typing import Iterable

import yaml
from flask import request


_CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "roles.yml"


def load_role_config() -> dict:
    with _CONFIG_PATH.open("r", encoding="utf-8") as stream:
        return yaml.safe_load(stream)


ROLE_CONFIG = load_role_config()
ROLE_PERMISSIONS = {
    role: set(details.get("permissions", []))
    for role, details in ROLE_CONFIG.get("roles", {}).items()
}


def role_label(role: str, locale: str = "en") -> str:
    details = ROLE_CONFIG.get("roles", {}).get(role, {})
    labels = details.get("label", {})
    return labels.get(locale, labels.get("en", role))


def normalize_locale(value: str | None) -> str:
    return "mn" if (value or "").lower().startswith("mn") else "en"


def has_permission(user: dict, permission: str) -> bool:
    role = user.get("role")
    permissions = ROLE_PERMISSIONS.get(role, set())
    if permission in permissions:
        return True
    # A scoped grant such as analytics.read.assigned satisfies the base guard;
    # resource ownership is checked by the endpoint/service layer afterwards.
    return any(grant.startswith(f"{permission}.") for grant in permissions)


def error_response(code: str, message: str, message_mn: str, status: int):
    locale = normalize_locale(request.headers.get("Accept-Language"))
    return {
        "error": {
            "code": code,
            "message": message_mn if locale == "mn" else message,
            "message_mn": message_mn,
        }
    }, status


def permission_required(permission: str):
    """Require a permission after token_required has attached the user."""
    def decorator(function):
        @wraps(function)
        def wrapped(current_user, *args, **kwargs):
            if not has_permission(current_user, permission):
                return error_response(
                    "permission_denied",
                    "You do not have permission to perform this action.",
                    "Танд энэ үйлдлийг хийх зөвшөөрөл байхгүй байна.",
                    403,
                )
            return function(current_user, *args, **kwargs)
        return wrapped
    return decorator


def any_permission_required(permissions: Iterable[str]):
    allowed = tuple(permissions)

    def decorator(function):
        @wraps(function)
        def wrapped(current_user, *args, **kwargs):
            if not any(has_permission(current_user, permission) for permission in allowed):
                return error_response(
                    "permission_denied",
                    "You do not have permission to perform this action.",
                    "Танд энэ үйлдлийг хийх зөвшөөрөл байхгүй байна.",
                    403,
                )
            return function(current_user, *args, **kwargs)
        return wrapped
    return decorator
