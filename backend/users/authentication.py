"""
Django Simple JWT Authentication for SkillBridge
=================================================

This module provides JWT authentication using django-rest-framework-simplejwt.

Flow:
1. User logs in via POST /api/v1/auth/login with email and password
2. Backend verifies credentials and generates access + refresh tokens
3. Frontend stores tokens and includes access_token in Authorization header: Bearer <token>
4. Simple JWT middleware automatically validates token on each request

JWT Payload:
{
    "user_id": 123,
    "email": "user@example.com",
    "iat": 1234567890,        # Issued at
    "exp": 1234571490,        # Expiration (1 hour)
    "jti": "unique-token-id"  # JWT ID for token tracking
}
"""

def user_authentication_rule(user):
    """
    Custom rule for validating if a user should be authenticated.
    
    Args:
        user: The Django User model instance
        
    Returns:
        bool: True if user is active and can be authenticated
    """
    return user is not None and user.is_active
