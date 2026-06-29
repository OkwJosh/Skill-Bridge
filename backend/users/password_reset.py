"""
Password reset flow.

Two-step:
  1. POST /auth/password/reset/         → email containing a tokenised URL
  2. POST /auth/password/confirm/       → uidb64 + token + new_password

The reset URL points at the FRONTEND (`FRONTEND_URL`/reset-password?uid=&token=).
The frontend captures the params, prompts for a new password, then POSTs to
/auth/password/confirm/ — which lives on the backend.

Token generation uses Django's PasswordResetTokenGenerator, which embeds the
user's last_login + password hash + pk in an HMAC. Tokens auto-invalidate when
the password changes or the user logs in.
"""

import logging
from typing import Optional

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import User


logger = logging.getLogger(__name__)

_token_generator = PasswordResetTokenGenerator()


# =============================================================================
# Public API
# =============================================================================

def request_password_reset(email: str) -> bool:
    """
    Send a password-reset email if a user with this email exists.

    Returns True if an email was sent, False if no user found. The CALLER
    must always return success to the client regardless — never leak which
    emails are registered.
    """
    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        logger.info('Password reset requested for non-existent email: %s', email)
        return False

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = _token_generator.make_token(user)

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    reset_url = f"{frontend_url}/reset-password?uid={uidb64}&token={token}"

    subject = 'SkillBridge: reset your password'
    body = (
        f"Hi{(' ' + user.full_name) if user.full_name else ''},\n\n"
        f"Someone (hopefully you) requested a password reset for the SkillBridge "
        f"account associated with this email.\n\n"
        f"Click the link below to choose a new password. If you didn't request this, "
        f"you can ignore this email.\n\n"
        f"{reset_url}\n\n"
        f"This link expires in 24 hours.\n\n"
        f"— SkillBridge"
    )

    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@skillbridge.local'),
        recipient_list=[user.email],
        fail_silently=False,
    )
    logger.info('Password reset email sent to user_id=%s', user.pk)
    return True


def confirm_password_reset(*, uidb64: str, token: str, new_password: str) -> Optional[User]:
    """
    Validate the (uidb64, token) pair and set the new password.

    Returns the User on success, None on any failure. Caller maps None → 400
    with a deliberately vague message so we don't leak whether uid or token
    was the problem.
    """
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

    if not _token_generator.check_token(user, token):
        return None

    if len(new_password) < 6:
        # Validation guard so callers can't bypass via the service layer.
        return None

    user.set_password(new_password)
    user.save(update_fields=['password'])
    return user
