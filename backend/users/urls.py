"""
User URL Routes for SkillBridge API
===================================

All routes prefixed with /api/v1/auth/ (configured in config/urls.py)

Authentication endpoints:
- POST /api/v1/auth/signup - Register new user
- POST /api/v1/auth/signin - Login with email/password (or use /login)
- POST /api/v1/auth/refresh - Refresh access token
- GET /api/v1/auth/me - Get current user profile
- PATCH /api/v1/auth/me - Update current user profile
"""

from django.urls import path
from .views import (
    AppleSignInView,
    EmailOtpRequestView,
    EmailOtpVerifyView,
    EmailResendVerificationView,
    EmailVerifyView,
    GoogleSignInView,
    HealthCheckView,
    MeView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    PasswordChangeView,
    SignInView,
    SignOutView,
    SignUpView,
    TokenRefreshView,
)

app_name = 'users'

urlpatterns = [
    # ── Authentication ──────────────────────────────────────────────────────
    path('signup/', SignUpView.as_view(), name='signup'),
    path('signin/', SignInView.as_view(), name='signin'),
    path('login/', SignInView.as_view(), name='login'),
    path('signout/', SignOutView.as_view(), name='signout'),
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),

    # ── Password reset ──────────────────────────────────────────────────────
    path('password/reset/', PasswordResetRequestView.as_view(), name='password-reset'),
    path('password/confirm/', PasswordResetConfirmView.as_view(), name='password-confirm'),
    path('password/change/', PasswordChangeView.as_view(), name='password-change'),

    # ── Email verification (link-based, web) ────────────────────────────────
    path('email/verify/', EmailVerifyView.as_view(), name='email-verify'),
    path('email/resend/', EmailResendVerificationView.as_view(), name='email-resend'),

    # ── Email OTP (numeric code, mobile) ────────────────────────────────────
    path('email/otp/request/', EmailOtpRequestView.as_view(), name='email-otp-request'),
    path('email/otp/verify/', EmailOtpVerifyView.as_view(), name='email-otp-verify'),

    # ── OAuth sign-in ───────────────────────────────────────────────────────
    path('google/', GoogleSignInView.as_view(), name='oauth-google'),
    path('apple/', AppleSignInView.as_view(), name='oauth-apple'),

    # ── User profile ────────────────────────────────────────────────────────
    path('me/', MeView.as_view(), name='me'),
]

