"""
User Views for SkillBridge API
==============================

Authentication and user profile endpoints.
All responses automatically wrapped in standard JSON envelope.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from .serializers import (
    UserMeSerializer, 
    UserUpdateSerializer,
    SignUpSerializer,
    SignInSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
    TokenRefreshSerializer
)
from .services import SupabaseAuthService, SupabaseAuthError


class SignUpView(APIView):
    """
    POST /api/v1/auth/signup
    
    Register a new user with email and password.
    Creates user in both Supabase Auth and Django.
    
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
            "refresh_token": "...",
            "expires_in": 3600
        }
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SignUpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            auth_service = SupabaseAuthService()
            user, tokens = auth_service.sign_up(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                full_name=serializer.validated_data.get('full_name', ''),
                role=serializer.validated_data.get('role', 'talent'),
                phone_number=serializer.validated_data.get('phone_number', ''),
                auto_confirm=True  # Skip email confirmation for testing
            )
            
            return Response({
                "user": UserMeSerializer(user).data,
                "access_token": tokens.get('access_token'),
                "refresh_token": tokens.get('refresh_token'),
                "expires_in": tokens.get('expires_in'),
                "token_type": tokens.get('token_type', 'bearer')
            }, status=status.HTTP_201_CREATED)
            
        except SupabaseAuthError as e:
            return Response(
                {"detail": e.message, "error_code": e.error_code},
                status=e.status_code
            )


class SignInView(APIView):
    """
    POST /api/v1/auth/signin
    
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
            "refresh_token": "...",
            "expires_in": 3600
        }
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = SignInSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            auth_service = SupabaseAuthService()
            user, tokens = auth_service.sign_in(
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password']
            )
            
            return Response({
                "user": UserMeSerializer(user).data,
                "access_token": tokens.get('access_token'),
                "refresh_token": tokens.get('refresh_token'),
                "expires_in": tokens.get('expires_in'),
                "token_type": tokens.get('token_type', 'bearer')
            })
            
        except SupabaseAuthError as e:
            return Response(
                {"detail": e.message, "error_code": e.error_code},
                status=e.status_code
            )


class SignOutView(APIView):
    """
    POST /api/v1/auth/signout
    
    Sign out the current user and invalidate their tokens.
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Get the access token from the request
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            access_token = auth_header.split(' ')[1]
            auth_service = SupabaseAuthService()
            auth_service.sign_out(access_token)
        
        return Response({"message": "Successfully signed out"})


class TokenRefreshView(APIView):
    """
    POST /api/v1/auth/refresh
    
    Refresh an expired access token using a refresh token.
    
    Request Body:
    {
        "refresh_token": "..."
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "access_token": "...",
            "refresh_token": "...",
            "expires_in": 3600
        }
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = TokenRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            auth_service = SupabaseAuthService()
            tokens = auth_service.refresh_token(
                refresh_token=serializer.validated_data['refresh_token']
            )
            
            return Response(tokens)
            
        except SupabaseAuthError as e:
            return Response(
                {"detail": e.message, "error_code": e.error_code},
                status=e.status_code
            )


class PasswordResetRequestView(APIView):
    """
    POST /api/v1/auth/password/reset
    
    Request a password reset email.
    
    Request Body:
    {
        "email": "user@example.com"
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "message": "Password reset email sent"
        }
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            auth_service = SupabaseAuthService()
            auth_service.reset_password_request(
                email=serializer.validated_data['email'],
                redirect_url=serializer.validated_data.get('redirect_url')
            )
            
            return Response({
                "message": "If an account with this email exists, a password reset link has been sent."
            })
            
        except SupabaseAuthError as e:
            # Don't reveal if email exists or not
            return Response({
                "message": "If an account with this email exists, a password reset link has been sent."
            })


class PasswordResetConfirmView(APIView):
    """
    POST /api/v1/auth/password/confirm
    
    Set a new password after clicking the reset link.
    The access_token is obtained from the reset link's URL fragment.
    
    Request Body:
    {
        "access_token": "...",  // From reset link
        "new_password": "newsecurepassword123"
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "message": "Password updated successfully"
        }
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            auth_service = SupabaseAuthService()
            auth_service.update_password(
                access_token=serializer.validated_data['access_token'],
                new_password=serializer.validated_data['new_password']
            )
            
            return Response({
                "message": "Password updated successfully"
            })
            
        except SupabaseAuthError as e:
            return Response(
                {"detail": e.message, "error_code": e.error_code},
                status=e.status_code
            )


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

