"""
Supabase JWT Authentication Backend for Django REST Framework
=============================================================

This module provides custom authentication for DRF that validates JWTs
issued by Supabase Auth.

Flow:
1. User logs in via frontend using Supabase Auth (Google, Email, etc.)
2. Frontend receives access_token from Supabase
3. Frontend sends API requests with header: Authorization: Bearer <access_token>
4. This backend decodes the JWT, verifies it, and returns the Django User

Supabase JWT Payload Structure:
{
    "aud": "authenticated",
    "exp": 1234567890,
    "sub": "uuid-of-user",          # Supabase user ID
    "email": "user@example.com",
    "role": "authenticated",
    "app_metadata": {...},
    "user_metadata": {...}
}
"""

import token

import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

from .models import User


class SupabaseJWTAuthentication(authentication.BaseAuthentication):
    """
    Custom DRF authentication class that validates Supabase JWT tokens.
    
    Usage:
        Add to DRF settings:
        REST_FRAMEWORK = {
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'users.authentication.SupabaseJWTAuthentication',
            ],
        }
    
    Headers:
        Authorization: Bearer <supabase_access_token>
    """
    
    # Keyword used in Authorization header
    keyword = 'Bearer'
    
    def authenticate(self, request):
        """
        Authenticate the request by validating the Supabase JWT.
        
        Args:
            request: The incoming DRF request
            
        Returns:
            Tuple of (user, token_payload) if authentication succeeds
            None if no authentication credentials provided
            
        Raises:
            AuthenticationFailed: If token is invalid or expired
        """
        # Extract the Authorization header
        auth_header = request.headers.get('Authorization', '')
        
        if not auth_header:
            # No auth header - allow other auth classes to try
            return None
        
        # Validate header format: "Bearer <token>"
        parts = auth_header.split()
        
        if len(parts) != 2 or parts[0] != self.keyword:
            # Invalid format - let other auth classes try
            return None
        
        token = parts[1]
        
        # Decode and verify the JWT
        payload = self._decode_jwt(token)
        
        # Get or create the Django user
        user = self._get_or_create_user(payload)
        
        # Return tuple of (user, auth_info)
        return (user, payload)
    
    def _decode_jwt(self, token: str) -> dict:
        try:
            # 1. Automatically fetch the Public Key from your Supabase project
            jwks_url = f"{settings.SUPABASE_URL}/auth/v1/.well-known/jwks.json"
            jwks_client = jwt.PyJWKClient(jwks_url)
            
            # 2. Find the exact key that matches the 'kid' in your token's header
            signing_key = jwks_client.get_signing_key_from_jwt(token)

            # 3. Decode the token using the Public Key and the ES256 algorithm
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=['ES256', 'RS256', 'HS256'], # Support modern AND legacy tokens
                options={"verify_aud": False}
            )
            return payload
            
        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired. Please refresh your session.')
        except jwt.InvalidTokenError as e:
            print(f"JWT ERROR: {str(e)}") 
            raise exceptions.AuthenticationFailed(f'Invalid token: {str(e)}')
        except Exception as e:
            print(f"UNEXPECTED JWT ERROR: {str(e)}")
            raise exceptions.AuthenticationFailed(f'Authentication error: {str(e)}')
    
    def _get_or_create_user(self, payload: dict) -> User:
        """
        Get existing Django user or create a new one based on Supabase JWT payload.
        
        The `sub` claim contains the Supabase user UUID, which we store as
        `supabase_uid` in our User model for linking.
        
        Args:
            payload: The decoded JWT payload
            
        Returns:
            User instance
            
        Raises:
            AuthenticationFailed: If required claims are missing
        """
        # Extract required claims from payload
        supabase_uid = payload.get('sub')
        email = payload.get('email', '')
        
        if not supabase_uid:
            raise exceptions.AuthenticationFailed(
                'Token missing required "sub" claim.'
            )
        
        # Extract optional user metadata from Supabase
        user_metadata = payload.get('user_metadata', {})
        full_name = user_metadata.get('full_name', '') or user_metadata.get('name', '')
        
        try:
            # Try to find existing user by Supabase UID
            user = User.objects.get(supabase_uid=supabase_uid)
            
            # Update email if it changed in Supabase
            if email and user.email != email:
                user.email = email
                user.save(update_fields=['email', 'updated_at'])
            
            return user
            
        except User.DoesNotExist:
            # Create new user - first time login via Supabase
            user = User.objects.create(
                supabase_uid=supabase_uid,
                email=email,
                username=email or supabase_uid,  # Use email as username, fallback to UID
                first_name=full_name,            # <--- THIS IS THE LINE TO FIX
                is_talent=True,  # Default role: new users are talents
            )
            return user
    
    def authenticate_header(self, request):
        """
        Return the WWW-Authenticate header value for 401 responses.
        
        Args:
            request: The incoming request
            
        Returns:
            String to be used as WWW-Authenticate header
        """
        return f'{self.keyword} realm="api"'
