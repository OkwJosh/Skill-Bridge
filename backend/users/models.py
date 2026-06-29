"""
Custom User Model for SkillBridge
==================================

Supports multiple roles per user via boolean flags.
Users are linked to Supabase Auth via the `supabase_uid` field.

Roles:
- Talent: Looking for opportunities (students, bootcamp grads, self-taught)
- Org Admin: Manages an organization posting opportunities
- Mentor: Runs guided projects and issues skill endorsements
- School Admin: Verifies academic records (Data Trust)

A user can have MULTIPLE roles simultaneously.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    
    Linked to Supabase Auth via `supabase_uid` which stores the
    Supabase user UUID (from the JWT 'sub' claim).
    """
    
    # =========================================================================
    # SUPABASE AUTH INTEGRATION
    # =========================================================================
    
    supabase_uid = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        db_index=True,
        help_text="UUID from Supabase Auth (JWT 'sub' claim)"
    )
    
    # =========================================================================
    # ROLE FLAGS - Users can have multiple roles simultaneously
    # =========================================================================
    
    is_talent = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Can apply for opportunities and build portfolio"
    )
    
    is_org_admin = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Can post opportunities for an organization"
    )
    
    is_mentor = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Can run guided projects and issue skill endorsements"
    )
    
    is_school_admin = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Can verify academic records as Data Trust admin"
    )
    
    # =========================================================================
    # PROFILE FIELDS
    # =========================================================================
    
    full_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="User's full display name"
    )
    
    phone_number = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number with country code"
    )
    
    avatar_url = models.URLField(
        blank=True,
        help_text="URL to profile photo (stored in Supabase Storage)"
    )

    # =========================================================================
    # EMAIL VERIFICATION
    # =========================================================================
    # Sign-up sets email_verified=False and emails a tokenised link. Login is
    # NOT blocked on this flag — the frontend surfaces a banner so the user
    # can still browse while we wait for them to click through.

    email_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="True once the user has clicked the verification link.",
    )

    email_verification_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the last verification email was sent. Drives resend rate-limiting.",
    )

    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.email or self.username
    
    @property
    def roles(self) -> list:
        """
        Return list of active role names for this user.
        
        Example: ['talent', 'mentor']
        """
        role_list = []
        if self.is_talent:
            role_list.append('talent')
        if self.is_org_admin:
            role_list.append('org_admin')
        if self.is_mentor:
            role_list.append('mentor')
        if self.is_school_admin:
            role_list.append('school_admin')
        return role_list
    
    @property
    def has_any_role(self) -> bool:
        """Check if user has at least one role assigned."""
        return any([self.is_talent, self.is_org_admin, self.is_mentor, self.is_school_admin])

    @property
    def needs_onboarding(self) -> bool:
        """True if the user has signed up but not yet picked a role."""
        return not self.has_any_role


class OAuthIdentity(models.Model):
    """
    Links a User to an external OAuth identity (Google, Apple, ...).

    Apple in particular may not return email on subsequent sign-ins, so we
    cannot rely on email for re-identification — `(provider, subject)` is the
    stable join key.
    """

    PROVIDER_GOOGLE = 'google'
    PROVIDER_APPLE = 'apple'
    PROVIDER_CHOICES = [
        (PROVIDER_GOOGLE, 'Google'),
        (PROVIDER_APPLE, 'Apple'),
    ]

    user = models.ForeignKey(
        'users.User',
        on_delete=models.CASCADE,
        related_name='oauth_identities',
    )
    provider = models.CharField(max_length=16, choices=PROVIDER_CHOICES, db_index=True)
    subject = models.CharField(
        max_length=255,
        help_text="The `sub` claim from the provider's ID token. Stable across sessions.",
    )

    # Snapshot at most-recent sign-in. Not used for auth, just for diagnostics.
    last_email = models.EmailField(blank=True)
    last_seen_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'oauth_identities'
        unique_together = [('provider', 'subject')]
        verbose_name = 'OAuth Identity'
        verbose_name_plural = 'OAuth Identities'

    def __str__(self):
        return f"{self.provider}:{self.subject} → {self.user.email}"

