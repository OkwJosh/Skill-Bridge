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
    - needs_onboarding: True if no role has been picked yet (post-OAuth signup)
    - Timestamps
    """

    roles = serializers.ReadOnlyField()
    needs_onboarding = serializers.ReadOnlyField()

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

            # Roles
            'roles',
            'is_talent',
            'is_org_admin',
            'is_mentor',
            'is_school_admin',
            'needs_onboarding',

            # Email verification
            'email_verified',

            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'email',
            'username',
            'roles',
            'needs_onboarding',
            'email_verified',
            'created_at',
            'updated_at',
        ]


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for PATCH /api/v1/auth/me

    Allows users to update their profile information.
    Role flags can be set (e.g., user declares they want to be a mentor).

    `is_school_admin` is self-declarable on signup/role-pick so a school
    admin can complete the post-OAuth ChooseRolePage flow. The first time
    that flag is set, the user is routed to /create-school which gates
    access to any school-side surface behind actually creating a School
    record. So setting the flag alone grants no power until the School
    exists and they're in `admins`.
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
            'is_school_admin',
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
    organization = serializers.DictField(required=False)
    
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
    Serializer for POST /api/v1/auth/signin or /api/v1/auth/login

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


# =============================================================================
# PASSWORD RESET
# =============================================================================

class PasswordResetRequestSerializer(serializers.Serializer):
    """POST /api/v1/auth/password/reset/"""
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """POST /api/v1/auth/password/confirm/"""
    uid = serializers.CharField(required=True)
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True, min_length=6, write_only=True,
        style={'input_type': 'password'},
    )


# =============================================================================
# OAUTH SIGN-IN
# =============================================================================

class OAuthSignInSerializer(serializers.Serializer):
    """POST /api/v1/auth/google/  and  POST /api/v1/auth/apple/

    Frontend obtains the ID token via Google Identity Services / Apple JS SDK
    and POSTs it here. Backend verifies + issues JWT.
    """
    id_token = serializers.CharField(required=True)
