"""
Supabase Auth Service
=====================
Handles all Supabase Auth operations: signup, login, password reset.

This service communicates with Supabase Auth API and syncs users with Django.
"""

import os
import requests
from typing import Optional, Tuple, Dict, Any
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class SupabaseAuthError(Exception):
    """Custom exception for Supabase Auth errors."""
    def __init__(self, message: str, status_code: int = 400, error_code: str = None):
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        super().__init__(self.message)


class SupabaseAuthService:
    """
    Service class for Supabase Auth operations.
    
    Usage:
        auth_service = SupabaseAuthService()
        
        # Sign up a new user
        user, tokens = auth_service.sign_up(
            email='user@example.com',
            password='securepassword123',
            full_name='John Doe',
            role='talent'
        )
        
        # Log in an existing user
        user, tokens = auth_service.sign_in(
            email='user@example.com',
            password='securepassword123'
        )
        
        # Reset password
        auth_service.reset_password(email='user@example.com')
    """
    
    def __init__(self):
        """Initialize with Supabase configuration."""
        self.supabase_url = getattr(settings, 'SUPABASE_URL', os.getenv('SUPABASE_URL'))
        self.supabase_anon_key = getattr(settings, 'SUPABASE_ANON_KEY', os.getenv('SUPABASE_ANON_KEY'))
        self.supabase_service_key = getattr(settings, 'SUPABASE_SERVICE_KEY', os.getenv('SUPABASE_SERVICE_KEY'))
        
        if not self.supabase_url or not self.supabase_anon_key:
            raise SupabaseAuthError(
                "SUPABASE_URL and SUPABASE_ANON_KEY must be configured",
                status_code=500,
                error_code="config_error"
            )
    
    def _get_headers(self, use_service_key: bool = False) -> Dict[str, str]:
        """Get headers for Supabase API requests."""
        key = self.supabase_service_key if use_service_key else self.supabase_anon_key
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json"
        }
    
    def _handle_supabase_error(self, response: requests.Response) -> None:
        """Parse and raise appropriate error from Supabase response."""
        try:
            error_data = response.json()
            error_message = (
                error_data.get('error_description') or 
                error_data.get('msg') or 
                error_data.get('message') or 
                error_data.get('error') or
                'Unknown error occurred'
            )
            error_code = error_data.get('error_code', 'unknown_error')
        except Exception:
            error_message = response.text or 'Unknown error occurred'
            error_code = 'unknown_error'
        
        raise SupabaseAuthError(
            message=error_message,
            status_code=response.status_code,
            error_code=error_code
        )
    
    def sign_up(
        self, 
        email: str, 
        password: str, 
        full_name: str = "",
        role: str = "talent",
        phone_number: str = "",
        auto_confirm: bool = True
    ) -> Tuple[User, Dict[str, Any]]:
        """
        Register a new user in Supabase Auth and create Django user.
        
        Args:
            email: User's email address
            password: User's password (min 6 characters)
            full_name: User's full display name
            role: Initial role ('talent', 'org_admin', 'mentor', 'school_admin')
            phone_number: Optional phone number
            auto_confirm: If True, skip email confirmation (for testing)
            
        Returns:
            Tuple of (Django User instance, tokens dict with access_token and refresh_token)
            
        Raises:
            SupabaseAuthError: If registration fails
        """
        # Validate inputs
        if not email or not password:
            raise SupabaseAuthError("Email and password are required", error_code="validation_error")
        
        if len(password) < 6:
            raise SupabaseAuthError("Password must be at least 6 characters", error_code="weak_password")
        
        valid_roles = ['talent', 'org_admin', 'mentor', 'school_admin']
        if role not in valid_roles:
            raise SupabaseAuthError(f"Invalid role. Must be one of: {valid_roles}", error_code="invalid_role")
        
        # Prepare Supabase signup payload
        url = f"{self.supabase_url}/auth/v1/signup"
        
        payload = {
            "email": email,
            "password": password,
            "data": {
                "full_name": full_name,
                "role": role,
                "phone_number": phone_number
            }
        }
        
        # Add option for auto-confirm (testing mode)
        if auto_confirm:
            payload["options"] = {"data": payload.pop("data")}
        
        # Make request to Supabase
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=10
        )
        
        if response.status_code not in [200, 201]:
            self._handle_supabase_error(response)
        
        data = response.json()
        
        # Extract user info from response
        supabase_user = data.get('user', {})
        supabase_uid = supabase_user.get('id')
        
        if not supabase_uid:
            raise SupabaseAuthError(
                "Failed to get user ID from Supabase",
                error_code="signup_failed"
            )
        
        # Create or update Django user
        django_user = self._sync_django_user(
            supabase_uid=supabase_uid,
            email=email,
            full_name=full_name,
            phone_number=phone_number,
            role=role
        )
        
        # Extract tokens
        tokens = {
            "access_token": data.get('access_token'),
            "refresh_token": data.get('refresh_token'),
            "expires_in": data.get('expires_in'),
            "token_type": data.get('token_type', 'bearer')
        }
        
        return django_user, tokens
    
    def sign_in(self, email: str, password: str) -> Tuple[User, Dict[str, Any]]:
        """
        Authenticate user with Supabase and return Django user with tokens.
        
        Args:
            email: User's email address
            password: User's password
            
        Returns:
            Tuple of (Django User instance, tokens dict)
            
        Raises:
            SupabaseAuthError: If authentication fails
        """
        if not email or not password:
            raise SupabaseAuthError("Email and password are required", error_code="validation_error")
        
        url = f"{self.supabase_url}/auth/v1/token?grant_type=password"
        
        payload = {
            "email": email,
            "password": password
        }
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            self._handle_supabase_error(response)
        
        data = response.json()
        
        # Extract user info
        supabase_user = data.get('user', {})
        supabase_uid = supabase_user.get('id')
        user_email = supabase_user.get('email', email)
        user_metadata = supabase_user.get('user_metadata', {})
        
        if not supabase_uid:
            raise SupabaseAuthError(
                "Failed to get user ID from Supabase",
                error_code="login_failed"
            )
        
        # Get or create Django user
        django_user = self._sync_django_user(
            supabase_uid=supabase_uid,
            email=user_email,
            full_name=user_metadata.get('full_name', ''),
            phone_number=user_metadata.get('phone_number', ''),
            role=user_metadata.get('role', 'talent')
        )
        
        # Extract tokens
        tokens = {
            "access_token": data.get('access_token'),
            "refresh_token": data.get('refresh_token'),
            "expires_in": data.get('expires_in'),
            "token_type": data.get('token_type', 'bearer')
        }
        
        return django_user, tokens
    
    def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: The refresh token from previous login
            
        Returns:
            New tokens dict with access_token and refresh_token
            
        Raises:
            SupabaseAuthError: If refresh fails
        """
        url = f"{self.supabase_url}/auth/v1/token?grant_type=refresh_token"
        
        payload = {
            "refresh_token": refresh_token
        }
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            self._handle_supabase_error(response)
        
        data = response.json()
        
        return {
            "access_token": data.get('access_token'),
            "refresh_token": data.get('refresh_token'),
            "expires_in": data.get('expires_in'),
            "token_type": data.get('token_type', 'bearer')
        }
    
    def reset_password_request(self, email: str, redirect_url: str = None) -> bool:
        """
        Request a password reset email.
        
        Args:
            email: User's email address
            redirect_url: URL to redirect after password reset (optional)
            
        Returns:
            True if request was successful
            
        Raises:
            SupabaseAuthError: If request fails
        """
        if not email:
            raise SupabaseAuthError("Email is required", error_code="validation_error")
        
        url = f"{self.supabase_url}/auth/v1/recover"
        
        payload = {"email": email}
        
        if redirect_url:
            payload["options"] = {"redirectTo": redirect_url}
        
        response = requests.post(
            url,
            headers=self._get_headers(),
            json=payload,
            timeout=10
        )
        
        if response.status_code not in [200, 204]:
            self._handle_supabase_error(response)
        
        return True
    
    def update_password(self, access_token: str, new_password: str) -> bool:
        """
        Update user's password (requires valid access token).
        
        Args:
            access_token: Valid access token (from reset link or current session)
            new_password: New password (min 6 characters)
            
        Returns:
            True if password was updated
            
        Raises:
            SupabaseAuthError: If update fails
        """
        if len(new_password) < 6:
            raise SupabaseAuthError("Password must be at least 6 characters", error_code="weak_password")
        
        url = f"{self.supabase_url}/auth/v1/user"
        
        headers = self._get_headers()
        headers["Authorization"] = f"Bearer {access_token}"
        
        payload = {"password": new_password}
        
        response = requests.put(
            url,
            headers=headers,
            json=payload,
            timeout=10
        )
        
        if response.status_code != 200:
            self._handle_supabase_error(response)
        
        return True
    
    def sign_out(self, access_token: str) -> bool:
        """
        Sign out user and invalidate their tokens.
        
        Args:
            access_token: User's current access token
            
        Returns:
            True if sign out was successful
        """
        url = f"{self.supabase_url}/auth/v1/logout"
        
        headers = self._get_headers()
        headers["Authorization"] = f"Bearer {access_token}"
        
        try:
            response = requests.post(url, headers=headers, timeout=10)
            return response.status_code in [200, 204]
        except Exception:
            return False
    
    def _sync_django_user(
        self,
        supabase_uid: str,
        email: str,
        full_name: str = "",
        phone_number: str = "",
        role: str = "talent"
    ) -> User:
        """
        Create or update Django user to sync with Supabase.
        
        Args:
            supabase_uid: Supabase user UUID
            email: User's email
            full_name: User's full name
            phone_number: User's phone number
            role: User's initial role
            
        Returns:
            Django User instance
        """
        # Set role flags based on role string
        role_flags = {
            'is_talent': role == 'talent',
            'is_org_admin': role == 'org_admin',
            'is_mentor': role == 'mentor',
            'is_school_admin': role == 'school_admin',
        }
        
        # Try to find existing user
        try:
            user = User.objects.get(supabase_uid=supabase_uid)
            
            # Update fields if changed
            updated = False
            if email and user.email != email:
                user.email = email
                updated = True
            if full_name and user.full_name != full_name:
                user.full_name = full_name
                updated = True
            if phone_number and user.phone_number != phone_number:
                user.phone_number = phone_number
                updated = True
            
            if updated:
                user.save()
            
            return user
            
        except User.DoesNotExist:
            # Create new user
            user = User.objects.create(
                supabase_uid=supabase_uid,
                email=email,
                username=email,
                full_name=full_name,
                phone_number=phone_number,
                **role_flags
            )
            return user
    
    def delete_user(self, supabase_uid: str) -> bool:
        """
        Delete user from both Supabase and Django (admin only).
        
        Args:
            supabase_uid: Supabase user UUID
            
        Returns:
            True if deletion was successful
            
        Raises:
            SupabaseAuthError: If deletion fails
        """
        if not self.supabase_service_key:
            raise SupabaseAuthError(
                "Service key required for user deletion",
                error_code="forbidden"
            )
        
        url = f"{self.supabase_url}/auth/v1/admin/users/{supabase_uid}"
        
        response = requests.delete(
            url,
            headers=self._get_headers(use_service_key=True),
            timeout=10
        )
        
        if response.status_code not in [200, 204]:
            self._handle_supabase_error(response)
        
        # Also delete Django user
        try:
            User.objects.filter(supabase_uid=supabase_uid).delete()
        except Exception:
            pass
        
        return True


# Singleton instance for convenience
auth_service = SupabaseAuthService()
