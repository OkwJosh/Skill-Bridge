"""
Organization Models for SkillBridge
====================================

Organizations post internships and micro-projects.
Members can have different roles (owner, admin, member).
"""

from django.db import models
from django.conf import settings


class Organization(models.Model):
    """
    Company or organization that posts opportunities.
    
    Organizations have:
    - Basic info (name, description, logo)
    - Industry classification
    - Verification status
    - Multiple members with different roles
    """
    
    # =========================================================================
    # BASIC INFO
    # =========================================================================
    
    name = models.CharField(
        max_length=255,
        help_text="Organization name"
    )
    
    slug = models.SlugField(
        max_length=255,
        unique=True,
        help_text="URL-friendly identifier"
    )
    
    description = models.TextField(
        blank=True,
        help_text="About the organization"
    )
    
    logo_url = models.URLField(
        blank=True,
        help_text="Organization logo URL (Supabase Storage)"
    )
    
    website_url = models.URLField(
        blank=True,
        help_text="Company website"
    )
    
    # =========================================================================
    # INDUSTRY & CLASSIFICATION
    # =========================================================================
    
    industry = models.ForeignKey(
        'core.CanonicalIndustry',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='organizations',
        help_text="Primary industry"
    )
    
    company_size = models.CharField(
        max_length=50,
        blank=True,
        choices=[
            ('1-10', '1-10 employees'),
            ('11-50', '11-50 employees'),
            ('51-200', '51-200 employees'),
            ('201-500', '201-500 employees'),
            ('501+', '501+ employees'),
        ],
        help_text="Company size range"
    )
    
    # =========================================================================
    # LOCATION
    # =========================================================================
    
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, default='Nigeria')
    
    # =========================================================================
    # VERIFICATION
    # =========================================================================
    
    is_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Organization has been verified by SkillBridge"
    )
    
    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        ordering = ['name']
        verbose_name = 'Organization'
        verbose_name_plural = 'Organizations'
    
    def __str__(self):
        return self.name


class OrganizationMember(models.Model):
    """
    Junction table for Organization membership.
    
    Users can belong to organizations with different roles.
    """
    
    class MemberRole(models.TextChoices):
        OWNER = 'owner', 'Owner'
        ADMIN = 'admin', 'Admin'
        MEMBER = 'member', 'Member'
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members'
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='organization_memberships'
    )
    
    role = models.CharField(
        max_length=20,
        choices=MemberRole.choices,
        default=MemberRole.MEMBER
    )
    
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'organization_members'
        unique_together = ['organization', 'user']
        verbose_name = 'Organization Member'
        verbose_name_plural = 'Organization Members'
    
    def __str__(self):
        return f"{self.user.email} - {self.organization.name} ({self.role})"

