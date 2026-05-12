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
    MeView, 
    HealthCheckView,
    SignUpView,
    SignInView,
    TokenRefreshView
)

app_name = 'users'

urlpatterns = [
    # ==========================================================================
    # AUTHENTICATION ENDPOINTS
    # ==========================================================================
    
    # POST /api/v1/auth/signup - Register new user
    path('signup/', SignUpView.as_view(), name='signup'),
    
    # POST /api/v1/auth/signin - Login with email/password
    path('signin/', SignInView.as_view(), name='signin'),
    
    # POST /api/v1/auth/login - Alternative login endpoint (same as signin)
    path('login/', SignInView.as_view(), name='login'),
    
    # POST /api/v1/auth/refresh - Refresh access token
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    
    # ==========================================================================
    # USER PROFILE ENDPOINT
    # ==========================================================================
    
    # GET  /api/v1/auth/me - Get current user's profile and roles
    # PATCH /api/v1/auth/me - Update current user's profile
    path('me/', MeView.as_view(), name='me'),
]

