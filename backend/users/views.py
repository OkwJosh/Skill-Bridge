"""
User Views for SkillBridge API
==============================

Authentication and user profile endpoints using Simple JWT.
All responses automatically wrapped in standard JSON envelope.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    UserMeSerializer,
    UserUpdateSerializer,
    SignUpSerializer,
    SignInSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    OAuthSignInSerializer,
)
from .password_reset import request_password_reset, confirm_password_reset
from .email_verification import (
    confirm_email,
    send_verification_email,
)
from .otp import (
    RESEND_COOLDOWN_SECONDS,
    send_email_otp,
    verify_email_otp,
)
from .oauth import (
    OAuthDisabledError,
    OAuthVerificationError,
    get_or_create_user_for_oauth,
    verify_apple_id_token,
    verify_google_id_token,
)


class SignUpView(APIView):
    """
    POST /api/v1/auth/signup
    
    Register a new user with email and password.
    Creates user in Django and returns JWT tokens.
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "securepassword123",
        "full_name": "John Doe",
        "role": "talent"  // talent, org_admin, mentor, school_admin
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "user": {...},
            "access_token": "...",
            "refresh_token": "..."
        }
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Create user
        user = User.objects.create_user(
            email=serializer.validated_data['email'],
            password=serializer.validated_data['password'],
            username=serializer.validated_data['email'],
            full_name=serializer.validated_data.get('full_name', ''),
        )
        
        # Set role
        role = serializer.validated_data.get('role', 'talent')
        if role == 'talent':
            user.is_talent = True
        elif role == 'org_admin':
            user.is_org_admin = True
        elif role == 'mentor':
            user.is_mentor = True
        elif role == 'school_admin':
            user.is_school_admin = True
        user.save()

        # Handle organization creation if role is org_admin and organization data is provided
        organization_data = serializer.validated_data.get('organization')
        if role == 'org_admin' and organization_data:
            from organizations.serializers import OrganizationUpdateSerializer
            from organizations.models import Organization, OrganizationMember
            from django.utils.text import slugify
            
            org_serializer = OrganizationUpdateSerializer(data=organization_data)
            org_serializer.is_valid(raise_exception=True)
            
            name = org_serializer.validated_data.get('name', '').strip()
            if name:
                base_slug = slugify(name)[:200] or 'org'
                slug = base_slug
                n = 2
                while Organization.objects.filter(slug=slug).exists():
                    slug = f'{base_slug}-{n}'
                    n += 1
                
                industry_id = org_serializer.validated_data.pop('industry_id', None)
                org = Organization.objects.create(slug=slug, **org_serializer.validated_data)
                
                if industry_id:
                    from core.models import CanonicalIndustry
                    ind = CanonicalIndustry.objects.filter(pk=industry_id, is_active=True).first()
                    if ind:
                        org.industry = ind
                        org.save(update_fields=['industry'])
                        
                OrganizationMember.objects.create(
                    organization=org, user=user,
                    role=OrganizationMember.MemberRole.OWNER,
                )

        # Fire-and-forget OTP email so the app can show the "Enter OTP" screen.
        # We don't block signup on email-server outages — the user can resend.
        try:
            send_email_otp(user)
        except Exception:  # noqa: BLE001
            import logging
            logging.getLogger(__name__).exception(
                'Failed to send verification OTP for user_id=%s', user.pk,
            )

        # Generate tokens
        refresh = RefreshToken.for_user(user)

        return Response({
            "user": UserMeSerializer(user).data,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        }, status=status.HTTP_201_CREATED)


class SignInView(APIView):
    """
    POST /api/v1/auth/signin (or /api/v1/auth/login)
    
    Authenticate user with email and password.
    Returns JWT tokens for API access.
    
    Request Body:
    {
        "email": "user@example.com",
        "password": "securepassword123"
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "user": {...},
            "access_token": "...",
            "refresh_token": "..."
        }
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Authenticate using email (not username)
        try:
            user = User.objects.get(email__iexact=email)
        except User.DoesNotExist:
            return Response(
                {"detail": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify password
        if not user.check_password(password):
            return Response(
                {"detail": "Invalid email or password"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate tokens
        refresh = RefreshToken.for_user(user)
        
        return Response({
            "user": UserMeSerializer(user).data,
            "access_token": str(refresh.access_token),
            "refresh_token": str(refresh),
        })



class TokenRefreshView(APIView):
    """
    POST /api/v1/auth/refresh/

    Refresh an expired access token using a refresh token.

    Request Body: {"refresh_token": "..."}   (also accepts "refresh")
    Response:     {"access_token": "...", "refresh_token": "...", "expires_in": 3600}
    """

    permission_classes = [AllowAny]

    def post(self, request):
        from rest_framework_simplejwt.tokens import RefreshToken
        from rest_framework_simplejwt.exceptions import TokenError
        from django.conf import settings as dj_settings

        raw = request.data.get('refresh_token') or request.data.get('refresh')
        if not raw:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 400},
                 'errors': [{'field': 'refresh_token',
                             'message': 'refresh_token is required.', 'code': 'required'}]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            refresh = RefreshToken(raw)
        except TokenError:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 401},
                 'errors': [{'field': None,
                             'message': 'Refresh token is invalid or expired.',
                             'code': 'token_invalid'}]},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        lifetime = dj_settings.SIMPLE_JWT.get('ACCESS_TOKEN_LIFETIME')
        return Response({
            'access_token': str(refresh.access_token),
            # ROTATE_REFRESH_TOKENS is False, so the same refresh token stays valid.
            'refresh_token': str(refresh),
            'expires_in': int(lifetime.total_seconds()) if lifetime else None,
        })



class MeView(APIView):
    """
    GET /api/v1/auth/me
    PATCH /api/v1/auth/me
    
    Retrieve or update the authenticated user's profile.
    
    This endpoint is called by the frontend immediately after login
    to get the user's context (roles, profile info, etc.)
    
    Response Format (via standard envelope):
    {
        "status": "success",
        "data": {
            "id": 1,
            "email": "user@example.com",
            "full_name": "John Doe",
            "roles": ["talent", "mentor"],
            "is_talent": true,
            "is_org_admin": false,
            "is_mentor": true,
            "is_school_admin": false,
            ...
        },
        "meta": {},
        "errors": []
    }
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/v1/auth/me
        
        Return the authenticated user's profile and roles.
        """
        serializer = UserMeSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        """
        PATCH /api/v1/auth/me
        
        Update the authenticated user's profile.
        Supports partial updates.
        """
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True  # Allow partial updates
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return the full updated profile
        return Response(UserMeSerializer(request.user).data)


class SignOutView(APIView):
    """
    POST /api/v1/auth/signout/

    With stateless JWT there is no server-side session to invalidate — the
    frontend clears its tokens on logout. This endpoint exists so the
    frontend's signout call doesn't 404; it returns a benign 200.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        return Response({'message': 'Signed out.'})


# =============================================================================
# PASSWORD RESET
# =============================================================================

class PasswordResetRequestView(APIView):
    """
    POST /api/v1/auth/password/reset/
    Body: {"email": "user@example.com"}

    Always returns 200 to avoid leaking which emails are registered.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request_password_reset(serializer.validated_data['email'])
        return Response({
            'message': (
                'If an account with this email exists, a password reset link '
                'has been sent.'
            ),
        })


class PasswordResetConfirmView(APIView):
    """
    POST /api/v1/auth/password/confirm/
    Body: {"uid": "<base64>", "token": "<token>", "new_password": "..."}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = confirm_password_reset(
            uidb64=serializer.validated_data['uid'],
            token=serializer.validated_data['token'],
            new_password=serializer.validated_data['new_password'],
        )
        if user is None:
            return Response(
                {'detail': 'Reset link is invalid or expired.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response({'message': 'Password updated. You can now log in.'})


class PasswordChangeView(APIView):
    """
    POST /api/v1/auth/password/change/
    Body: {"old_password": "...", "new_password": "..."}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        old_password = request.data.get('old_password')
        new_password = request.data.get('new_password')

        if not old_password or not new_password:
            return Response(
                {'detail': 'Old and new passwords are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.check_password(old_password):
            return Response(
                {'detail': 'Incorrect old password.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(new_password) < 6:
            return Response(
                {'detail': 'New password must be at least 6 characters.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.user.set_password(new_password)
        request.user.save()
        
        return Response({'message': 'Password changed successfully.'})

# =============================================================================
# EMAIL VERIFICATION
# =============================================================================

class EmailVerifyView(APIView):
    """
    POST /api/v1/auth/email/verify/
    Body: {"uid": "<base64>", "token": "<token>"}
    """
    permission_classes = [AllowAny]

    def post(self, request):
        uid = (request.data.get('uid') or '').strip()
        token = (request.data.get('token') or '').strip()
        if not uid or not token:
            return Response(
                {'detail': 'uid and token are required.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = confirm_email(uidb64=uid, token=token)
        if user is None:
            return Response(
                {'detail': 'Verification link is invalid or expired.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response({
            'message': 'Email verified.',
            'email_verified': True,
        })


class EmailResendVerificationView(APIView):
    """
    POST /api/v1/auth/email/resend/

    Resends the verification email to the authenticated user. Subject to
    the cooldown defined in email_verification.RESEND_COOLDOWN.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.email_verified:
            return Response({'message': 'Email is already verified.'})
        sent = send_verification_email(request.user)
        if not sent:
            return Response(
                {'detail': 'Please wait a couple of minutes before resending.'},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        return Response({'message': 'Verification email sent.'})


# =============================================================================
# EMAIL OTP (numeric code — mobile)
# =============================================================================

class EmailOtpRequestView(APIView):
    """
    POST /api/v1/auth/email/otp/request/

    (Re)send a numeric verification code to the authenticated user's email.
    Subject to a short resend cooldown.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if request.user.email_verified:
            return Response({'message': 'Email is already verified.', 'email_verified': True})

        sent, wait = send_email_otp(request.user)
        if not sent and wait > 0:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 429},
                 'errors': [{'field': None,
                             'message': f'Please wait {wait}s before requesting a new code.',
                             'code': 'resend_cooldown'}]},
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )
        return Response({'message': 'Verification code sent.', 'resend_in': RESEND_COOLDOWN_SECONDS})


class EmailOtpVerifyView(APIView):
    """
    POST /api/v1/auth/email/otp/verify/
    Body: {"code": "1234"}
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        code = str(request.data.get('code') or '').strip()
        if not code:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 400},
                 'errors': [{'field': 'code', 'message': 'Code is required.', 'code': 'required'}]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ok, err = verify_email_otp(request.user, code)
        if ok:
            return Response({'message': 'Email verified.', 'email_verified': True})

        messages = {
            'expired': 'This code has expired. Request a new one.',
            'too_many_attempts': 'Too many incorrect attempts. Request a new code.',
            'invalid': 'That code is incorrect.',
        }
        http = status.HTTP_429_TOO_MANY_REQUESTS if err == 'too_many_attempts' \
            else status.HTTP_400_BAD_REQUEST
        return Response(
            {'status': 'error', 'data': None,
             'meta': {'http_status': http},
             'errors': [{'field': 'code',
                         'message': messages.get(err, 'Verification failed.'),
                         'code': err or 'invalid'}]},
            status=http,
        )


# =============================================================================
# OAUTH SIGN-IN (Google + Apple)
# =============================================================================

def _oauth_error_response(exc: OAuthDisabledError | OAuthVerificationError) -> Response:
    """Map oauth exceptions to the envelope."""
    if isinstance(exc, OAuthDisabledError):
        return Response(
            {
                'status': 'error', 'data': None,
                'meta': {'http_status': 503, 'error_type': 'OAuthDisabledError'},
                'errors': [{
                    'field': None, 'message': str(exc), 'code': 'oauth_disabled',
                }],
            },
            status=503,
        )
    return Response(
        {
            'status': 'error', 'data': None,
            'meta': {'http_status': 401, 'error_type': 'OAuthVerificationError'},
            'errors': [{
                'field': None, 'message': 'Invalid OAuth token.', 'code': 'oauth_invalid_token',
            }],
        },
        status=401,
    )


def _issue_jwt_for_oauth_user(user) -> Response:
    """Common tail for both Google and Apple sign-in."""
    refresh = RefreshToken.for_user(user)
    return Response({
        'user': UserMeSerializer(user).data,
        'access_token': str(refresh.access_token),
        'refresh_token': str(refresh),
    })


class GoogleSignInView(APIView):
    """POST /api/v1/auth/google/  Body: {"id_token": "<google id token>"}"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OAuthSignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            identity = verify_google_id_token(serializer.validated_data['id_token'])
            user, _created = get_or_create_user_for_oauth(identity)
        except (OAuthDisabledError, OAuthVerificationError) as exc:
            return _oauth_error_response(exc)
        return _issue_jwt_for_oauth_user(user)


class AppleSignInView(APIView):
    """POST /api/v1/auth/apple/  Body: {"id_token": "<apple id token>"}"""
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = OAuthSignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            identity = verify_apple_id_token(serializer.validated_data['id_token'])
            user, _created = get_or_create_user_for_oauth(identity)
        except (OAuthDisabledError, OAuthVerificationError) as exc:
            return _oauth_error_response(exc)
        return _issue_jwt_for_oauth_user(user)


class HealthCheckView(APIView):
    """
    GET /api/v1/health
    
    Simple health check endpoint for load balancers and monitoring.
    No authentication required.
    """
    
    permission_classes = [AllowAny]
    
    def get(self, request):
        """Return service health status."""
        return Response({
            'service': 'skillbridge-api',
            'status': 'healthy',
            'version': '1.0.0',
        })

