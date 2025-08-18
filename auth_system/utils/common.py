from datetime import timedelta
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import CommonPasswordValidator
import re


def token_expiry_time():
    """Returns access token expiry datetime based on SIMPLE_JWT settings."""
    minutes = (
        settings.SIMPLE_JWT.get(
            "ACCESS_TOKEN_LIFETIME", timedelta(minutes=30)
        ).total_seconds()
        / 60
    )
    return timezone.now() + timedelta(minutes=minutes)


def refresh_token_expiry_time():
    """Returns refresh token expiry datetime based on SIMPLE_JWT settings."""
    duration = settings.SIMPLE_JWT.get("REFRESH_TOKEN_LIFETIME", timedelta(days=7))
    return timezone.now() + duration


def validate_password(password):
    errors = []

    if len(password) < 8:
        errors.append("Password must be at least 8 characters long.")
    if not re.search(r"[A-Z]", password):
        errors.append("Password must contain at least one uppercase letter.")
    if not re.search(r"[a-z]", password):
        errors.append("Password must contain at least one lowercase letter.")
    if not re.search(r"\d", password):
        errors.append("Password must contain at least one digit.")
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        errors.append("Password must contain at least one special character.")

    try:
        common_validator = CommonPasswordValidator()
        common_validator.validate(password)
    except ValidationError as e:
        errors.extend(e.messages)

    if errors:
        raise ValidationError(errors)


def get_client_ip_and_agent(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    ip = (
        x_forwarded_for.split(",")[0].strip()
        if x_forwarded_for
        else request.META.get("REMOTE_ADDR", "127.0.0.1")
    )
    agent = request.META.get("HTTP_USER_AGENT", "Unknown")
    return ip, agent
