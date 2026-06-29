"""
OAuth ID-token verification for Sign in with Google / Apple.

Pattern: the frontend obtains an ID token directly from the provider's JS SDK
and sends it to the backend. The backend verifies the signature + claims and
issues its own JWT pair (same Simple JWT we use for password sign-in).

Missing credentials → OAuthDisabledError → 503 ai_disabled-style response.
Invalid token   → OAuthVerificationError → 401.
"""

import logging
import os
from dataclasses import dataclass
from typing import Optional

import jwt
import requests
from django.conf import settings


logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions (mapped to HTTP codes in views.py)
# =============================================================================

class OAuthError(Exception):
    """Base class for all OAuth failures."""


class OAuthDisabledError(OAuthError):
    """Required client ID env var is missing — provider is not configured."""


class OAuthVerificationError(OAuthError):
    """Token signature, audience, issuer, or expiry check failed."""


# =============================================================================
# Result type
# =============================================================================

@dataclass
class OAuthVerifiedIdentity:
    """The minimum we need from a verified ID token."""
    provider: str         # 'google' | 'apple'
    subject: str          # the `sub` claim — stable join key
    email: Optional[str]
    email_verified: bool
    name: str = ''        # may be empty (Apple often omits)
    picture: str = ''     # may be empty


# =============================================================================
# Google
# =============================================================================

def verify_google_id_token(token: str) -> OAuthVerifiedIdentity:
    """
    Verify a Google ID token using the google-auth library.

    Validates signature, expiry, issuer (`accounts.google.com` /
    `https://accounts.google.com`), and audience (== our client ID).
    """
    client_id = os.environ.get('GOOGLE_OAUTH_CLIENT_ID')
    if not client_id:
        raise OAuthDisabledError('Google Sign In is not configured on this server.')

    try:
        # Imported lazily so a missing google-auth doesn't crash Django boot.
        from google.auth.transport import requests as g_requests
        from google.oauth2 import id_token
    except ImportError as exc:
        raise OAuthDisabledError('google-auth library not installed.') from exc

    try:
        idinfo = id_token.verify_oauth2_token(token, g_requests.Request(), client_id)
    except ValueError as exc:
        raise OAuthVerificationError(f'Invalid Google ID token: {exc}') from exc

    return OAuthVerifiedIdentity(
        provider='google',
        subject=idinfo['sub'],
        email=idinfo.get('email'),
        email_verified=bool(idinfo.get('email_verified', False)),
        name=idinfo.get('name', ''),
        picture=idinfo.get('picture', ''),
    )


# =============================================================================
# Apple
# =============================================================================

_APPLE_KEYS_URL = 'https://appleid.apple.com/auth/keys'
_APPLE_ISSUER = 'https://appleid.apple.com'

# PyJWKClient caches keys internally; reuse a single instance per process.
_apple_jwks_client: Optional[jwt.PyJWKClient] = None


def _get_apple_jwks_client() -> jwt.PyJWKClient:
    global _apple_jwks_client
    if _apple_jwks_client is None:
        _apple_jwks_client = jwt.PyJWKClient(_APPLE_KEYS_URL)
    return _apple_jwks_client


def verify_apple_id_token(token: str) -> OAuthVerifiedIdentity:
    """
    Verify an Apple ID token (JWT signed by Apple's published JWKS).

    Validates signature against Apple's JWKS, expiry, issuer, and audience
    (== our Service ID, e.g. `com.skillbridge.web`).

    Apple often omits `email` on subsequent sign-ins after the first. The
    caller MUST re-identify the user via `(provider='apple', subject)` rather
    than email.
    """
    service_id = os.environ.get('APPLE_SERVICE_ID')
    if not service_id:
        raise OAuthDisabledError('Apple Sign In is not configured on this server.')

    try:
        signing_key = _get_apple_jwks_client().get_signing_key_from_jwt(token)
        idinfo = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            audience=service_id,
            issuer=_APPLE_ISSUER,
        )
    except (jwt.InvalidTokenError, jwt.PyJWKClientError, requests.RequestException) as exc:
        raise OAuthVerificationError(f'Invalid Apple ID token: {exc}') from exc

    email_verified = idinfo.get('email_verified')
    if isinstance(email_verified, str):
        # Apple sometimes returns the string "true" / "false".
        email_verified = email_verified.lower() == 'true'

    return OAuthVerifiedIdentity(
        provider='apple',
        subject=idinfo['sub'],
        email=idinfo.get('email'),
        email_verified=bool(email_verified),
        # Apple never returns name in the ID token (the name is delivered
        # separately on first sign-in via the `user` form-encoded field).
        name='',
        picture='',
    )


# =============================================================================
# OAuth → Django User upsert
# =============================================================================

def get_or_create_user_for_oauth(identity: OAuthVerifiedIdentity):
    """
    Find or create a User for a verified OAuth identity.

    Resolution order:
      1. Existing OAuthIdentity row with (provider, subject) → its user
      2. Existing User by email (case-insensitive) → link a new OAuthIdentity
      3. Create new User + new OAuthIdentity

    Returns (User, created: bool).
    """
    from .models import OAuthIdentity, User

    # 1. Already-linked
    existing = (
        OAuthIdentity.objects
        .select_related('user')
        .filter(provider=identity.provider, subject=identity.subject)
        .first()
    )
    if existing:
        # Refresh last_email snapshot if we have one.
        if identity.email and existing.last_email != identity.email:
            existing.last_email = identity.email
            existing.save(update_fields=['last_email', 'last_seen_at'])
        return existing.user, False

    # 2. Email match → link the existing account.
    user = None
    if identity.email:
        user = User.objects.filter(email__iexact=identity.email).first()

    created = False
    if user is None:
        # 3. Brand-new user. No password (OAuth-only until they request reset).
        if not identity.email:
            # Apple subsequent-signin with no email AND no linked identity —
            # we can't safely create a user without a unique identifier.
            raise OAuthVerificationError(
                'OAuth provider returned no email and no prior linked account.'
            )
        user = User.objects.create_user(
            username=identity.email,
            email=identity.email,
            full_name=identity.name or '',
            avatar_url=identity.picture or '',
        )
        user.set_unusable_password()
        user.save(update_fields=['password'])
        created = True

    OAuthIdentity.objects.create(
        user=user,
        provider=identity.provider,
        subject=identity.subject,
        last_email=identity.email or '',
    )
    return user, created
