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
    SignInSerializer
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
    POST /api/v1/auth/refresh
    
    Refresh an expired access token using a refresh token.
    
    Request Body:
    {
        "refresh": "..."
    }
    
    Response:
    {
        "status": "success",
        "data": {
            "access": "..."
        }
    }
    """
    
    permission_classes = [AllowAny]
    
    def post(self, request):
        from rest_framework_simplejwt.serializers import TokenRefreshSerializer as JWTRefreshSerializer
        
        serializer = JWTRefreshSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        return Response(serializer.validated_data)



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

