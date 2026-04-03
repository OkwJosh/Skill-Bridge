"""
User URL Routes for SkillBridge API
===================================

All routes prefixed with /api/v1/auth/ (configured in config/urls.py)
"""

from django.urls import path
from .views import (
    MeView, 
    HealthCheckView,
    SignUpView,
    SignInView,
    SignOutView,
    TokenRefreshView,
    PasswordResetRequestView,
    PasswordResetConfirmView
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
    
    # POST /api/v1/auth/signout - Logout current user
    path('signout/', SignOutView.as_view(), name='signout'),
    
    # POST /api/v1/auth/refresh - Refresh access token
    path('refresh/', TokenRefreshView.as_view(), name='refresh'),
    
    # ==========================================================================
    # PASSWORD RESET ENDPOINTS
    # ==========================================================================
    
    # POST /api/v1/auth/password/reset - Request password reset email
    path('password/reset/', PasswordResetRequestView.as_view(), name='password_reset'),
    
    # POST /api/v1/auth/password/confirm - Set new password
    path('password/confirm/', PasswordResetConfirmView.as_view(), name='password_confirm'),
    
    # ==========================================================================
    # USER PROFILE ENDPOINT
    # ==========================================================================
    
    # GET  /api/v1/auth/me - Get current user's profile and roles
    # PATCH /api/v1/auth/me - Update current user's profile
    path('me/', MeView.as_view(), name='me'),
]
