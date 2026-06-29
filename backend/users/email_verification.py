"""
Email verification flow.

Two-step:
  1. POST /auth/email/resend/  → email containing tokenised URL (uid+token)
  2. POST /auth/email/verify/  → uid + token → sets email_verified=True

The verification URL points at the FRONTEND:
    {FRONTEND_URL}/verify-email?uid=&token=
The frontend captures the params and POSTs to the backend.

Tokens use Django's PasswordResetTokenGenerator subclassed with a custom
salt so a password-reset token can't be replayed as a verification token
and vice versa. Tokens auto-invalidate when the user's email_verified
flag flips (it's part of the HMAC payload).
"""

import logging
from datetime import timedelta
from typing import Optional

from django.conf import settings
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode

from .models import User

logger = logging.getLogger(__name__)


class _EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    """
    Identical to PasswordResetTokenGenerator but with a different key salt
    so its tokens can't substitute for password-reset tokens.

    `_make_hash_value` mixes user.pk + email + email_verified into the HMAC
    so the token rotates the moment the email is verified (preventing a
    leaked link from being replayed once the user clicks it).
    """
    key_salt = 'users.email_verification.EmailVerificationTokenGenerator'

    def _make_hash_value(self, user, timestamp):
        return f'{user.pk}{user.email}{user.email_verified}{timestamp}'


_token_generator = _EmailVerificationTokenGenerator()

# Resend cooldown — don't let a frontend bug pummel the SMTP server.
RESEND_COOLDOWN = timedelta(minutes=2)


def send_verification_email(user: User) -> bool:
    """
    Send a verification email if the user is not already verified.

    Returns True if an email went out, False if the user was already
    verified or we're within the resend cooldown.
    """
    if user.email_verified:
        return False

    if user.email_verification_sent_at and (
        timezone.now() - user.email_verification_sent_at < RESEND_COOLDOWN
    ):
        return False

    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = _token_generator.make_token(user)

    frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:5173').rstrip('/')
    verify_url = f'{frontend_url}/verify-email?uid={uidb64}&token={token}'

    subject = 'SkillBridge: confirm your email'
    body = (
        f"Hi{(' ' + user.full_name) if user.full_name else ''},\n\n"
        f"Welcome to SkillBridge. Please confirm your email by clicking the link below:\n\n"
        f"{verify_url}\n\n"
        f"If you didn't create this account, you can safely ignore this email.\n\n"
        f"— SkillBridge"
    )

    send_mail(
        subject=subject,
        message=body,
        from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'no-reply@skillbridge.local'),
        recipient_list=[user.email],
        fail_silently=False,
    )
    user.email_verification_sent_at = timezone.now()
    user.save(update_fields=['email_verification_sent_at'])
    logger.info('Verification email sent to user_id=%s', user.pk)
    return True


def confirm_email(*, uidb64: str, token: str) -> Optional[User]:
    """Validate (uidb64, token) and flip email_verified=True. Returns user or None."""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return None

    if user.email_verified:
        # Already verified — return the user so the frontend can land them
        # on the success state without re-flipping the flag.
        return user

    if not _token_generator.check_token(user, token):
        return None

    user.email_verified = True
    user.save(update_fields=['email_verified'])
    return user
