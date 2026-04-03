"""
User Serializers for SkillBridge API
====================================

Serializers for user authentication and profile endpoints.
All responses follow the standard envelope via the custom renderer.
"""

from rest_framework import serializers
from .models import User


class UserMeSerializer(serializers.ModelSerializer):
    """
    Serializer for GET /api/v1/auth/me
    
    Returns the authenticated user's profile, including:
    - Basic info (id, email, full_name)
    - Role flags and computed roles list
    - Timestamps
    
    This is the first API call the frontend makes after login to
    understand the user's context and available features.
    """
    
    # Computed field from model property
    roles = serializers.ReadOnlyField()
    
    class Meta:
        model = User
        fields = [
            # Identity
            'id',
            'email',
            'username',
            'full_name',
            'phone_number',
            'avatar_url',
            
            # Roles - both flags and computed list
            'roles',  # ['talent', 'mentor'] - computed
            'is_talent',
            'is_org_admin',
            'is_mentor',
            'is_school_admin',
            
            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'email',
            'username',
            'roles',
            'created_at',
            'updated_at',
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for PATCH /api/v1/auth/me
    
    Allows users to update their profile information.
    Role flags can be set (e.g., user declares they want to be a mentor).
    
    Note: is_school_admin should only be set by superusers, not self-service.
    """
    
    class Meta:
        model = User
        fields = [
            'full_name',
            'phone_number',
            'avatar_url',
            # Users can self-declare these roles
            'is_talent',
            'is_org_admin',
            'is_mentor',
            # is_school_admin intentionally excluded - admin-only
        ]
    
    def validate_phone_number(self, value):
        """Basic phone number validation."""
        if value:
            # Remove spaces and dashes for storage
            cleaned = value.replace(' ', '').replace('-', '')
            if not cleaned.replace('+', '').isdigit():
                raise serializers.ValidationError(
                    "Phone number must contain only digits, spaces, dashes, and optional + prefix."
                )
            return cleaned
        return value


class UserRolesSerializer(serializers.Serializer):
    """
    Lightweight serializer for just returning roles.
    Used for quick role checks without full profile.
    """
    
    id = serializers.IntegerField(read_only=True)
    roles = serializers.ListField(read_only=True)
    is_talent = serializers.BooleanField(read_only=True)
    is_org_admin = serializers.BooleanField(read_only=True)
    is_mentor = serializers.BooleanField(read_only=True)
    is_school_admin = serializers.BooleanField(read_only=True)


# =============================================================================
# AUTHENTICATION SERIALIZERS
# =============================================================================

class SignUpSerializer(serializers.Serializer):
    """
    Serializer for POST /api/v1/auth/signup
    
    Validates registration data before creating user in Supabase and Django.
    """
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        min_length=6,
        write_only=True,
        style={'input_type': 'password'}
    )
    full_name = serializers.CharField(required=False, max_length=255, allow_blank=True)
    phone_number = serializers.CharField(required=False, max_length=20, allow_blank=True)
    role = serializers.ChoiceField(
        choices=['talent', 'org_admin', 'mentor', 'school_admin'],
        default='talent',
        required=False
    )
    
    def validate_email(self, value):
        """Check if email is already registered in Django."""
        if User.objects.filter(email__iexact=value).exists():
            raise serializers.ValidationError("An account with this email already exists.")
        return value.lower()
    
    def validate_password(self, value):
        """Ensure password meets minimum requirements."""
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters.")
        return value


class SignInSerializer(serializers.Serializer):
    """
    Serializer for POST /api/v1/auth/signin
    
    Validates login credentials.
    """
    
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_email(self, value):
        return value.lower()


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for POST /api/v1/auth/refresh
    
    Validates refresh token request.
    """
    
    refresh_token = serializers.CharField(required=True)


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for POST /api/v1/auth/password/reset
    
    Validates password reset request.
    """
    
    email = serializers.EmailField(required=True)
    redirect_url = serializers.URLField(required=False, allow_blank=True)
    
    def validate_email(self, value):
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for POST /api/v1/auth/password/confirm
    
    Validates new password after reset.
    """
    
    access_token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        min_length=6,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """Ensure password meets minimum requirements."""
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters.")
        return value
