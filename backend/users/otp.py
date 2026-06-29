"""
Email OTP verification (numeric code).
======================================

A mobile-friendly alternative to the link-based flow in
``email_verification.py``. The app shows a 4-digit code entry screen
(``Enter OTP``); this module mints, emails, and checks those codes.

State lives in Django's cache (no DB migration): the code is stored
*hashed* with a TTL, alongside a resend-cooldown marker and an attempt
counter. Verifying a correct code flips the existing ``User.email_verified``
row field — that's a normal row update, not a schema change.

NOTE: the default LocMemCache is per-process. A single ``runserver`` (or any
single-worker deployment) is fine; a multi-worker prod deployment should point
``CACHES`` at Redis so codes are visible across workers.
"""

import logging
import secrets

from django.conf import settings
from django.contrib.auth.hashers import check_password, make_password
from django.core.cache import cache
from django.core.mail import send_mail
from django.utils import timezone

from .models import User

logger = logging.getLogger(__name__)

OTP_LENGTH = 4                 # matches the 4-box UI
OTP_TTL_SECONDS = 600          # code valid for 10 minutes
RESEND_COOLDOWN_SECONDS = 45   # matches the "resend in 45 s" UI
MAX_ATTEMPTS = 5               # wrong tries before the code is burned


def _code_key(uid: int) -> str:
    return f'email_otp:code:{uid}'


def _sent_key(uid: int) -> str:
    return f'email_otp:sent:{uid}'


def _attempts_key(uid: int) -> str:
    return f'email_otp:attempts:{uid}'


def _generate_code() -> str:
    return f'{secrets.randbelow(10 ** OTP_LENGTH):0{OTP_LENGTH}d}'


def seconds_until_resend(user: User) -> int:
    """Remaining cooldown before another code may be requested."""
    sent_at = cache.get(_sent_key(user.id))
    if not sent_at:
        return 0
    elapsed = (timezone.now() - sent_at).total_seconds()
    return max(0, int(RESEND_COOLDOWN_SECONDS - elapsed))


def send_email_otp(user: User) -> tuple[bool, int]:
    """
    Mint + email a fresh code.

    Returns ``(sent, wait_seconds)``:
      - (True, RESEND_COOLDOWN_SECONDS) when an email went out
      - (False, remaining) when still within the resend cooldown
      - (False, 0) when the user is already verified
    """
    if user.email_verified:
        return (False, 0)

    remaining = seconds_until_resend(user)
    if remaining > 0:
        return (False, remaining)

    code = _generate_code()
    cache.set(_code_key(user.id), make_password(code), OTP_TTL_SECONDS)
    cache.set(_sent_key(user.id), timezone.now(), RESEND_COOLDOWN_SECONDS)
    cache.set(_attempts_key(user.id), 0, OTP_TTL_SECONDS)

    subject = 'Your SkillBridge verification code'
    body = (
        f"Hi{(' ' + user.full_name) if user.full_name else ''},\n\n"
        f"Your SkillBridge verification code is: {code}\n\n"
        f"It expires in {OTP_TTL_SECONDS // 60} minutes. If you didn't request "
        f"this, you can ignore this email.\n\n— SkillBridge"
    )
    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@skillbridge.local'),
        recipient_list=[user.email],
        fail_silently=False,
    )
    logger.info('Email OTP sent to user_id=%s', user.pk)
    return (True, RESEND_COOLDOWN_SECONDS)


def verify_email_otp(user: User, code: str) -> tuple[bool, str | None]:
    """
    Check a submitted code.

    Returns ``(ok, error_code)`` where error_code is one of
    ``expired`` | ``too_many_attempts`` | ``invalid`` | None.
    """
    if user.email_verified:
        return (True, None)

    hashed = cache.get(_code_key(user.id))
    if not hashed:
        return (False, 'expired')

    attempts = cache.get(_attempts_key(user.id)) or 0
    if attempts >= MAX_ATTEMPTS:
        cache.delete(_code_key(user.id))
        return (False, 'too_many_attempts')

    if not check_password(code, hashed):
        cache.set(_attempts_key(user.id), attempts + 1, OTP_TTL_SECONDS)
        return (False, 'invalid')

    # Success — burn the code and flip the flag.
    cache.delete(_code_key(user.id))
    cache.delete(_attempts_key(user.id))
    cache.delete(_sent_key(user.id))
    user.email_verified = True
    user.save(update_fields=['email_verified'])
    logger.info('Email verified via OTP for user_id=%s', user.pk)
    return (True, None)
