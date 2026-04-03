"""
User Admin Configuration
========================

Customized Django Admin for the User model with role management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    Admin interface for User model.
    
    Extends the default UserAdmin with:
    - Role flag management
    - Supabase UID display
    - Custom list filters
    """
    
    # List display
    list_display = [
        'email',
        'full_name',
        'is_talent',
        'is_org_admin',
        'is_mentor',
        'is_school_admin',
        'is_active',
        'created_at',
    ]
    
    # Filters in sidebar
    list_filter = [
        'is_talent',
        'is_org_admin',
        'is_mentor',
        'is_school_admin',
        'is_active',
        'is_staff',
        'created_at',
    ]
    
    # Search fields
    search_fields = ['email', 'full_name', 'username', 'supabase_uid']
    
    # Default ordering
    ordering = ['-created_at']
    
    # Editable directly from list view
    list_editable = ['is_talent', 'is_org_admin', 'is_mentor', 'is_school_admin']
    
    # Fields shown when viewing/editing a user
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Supabase Integration', {
            'fields': ('supabase_uid',),
            'classes': ('collapse',),  # Collapsed by default
        }),
        ('SkillBridge Roles', {
            'fields': ('is_talent', 'is_org_admin', 'is_mentor', 'is_school_admin'),
            'description': 'A user can have multiple roles simultaneously.',
        }),
        ('Profile', {
            'fields': ('full_name', 'phone_number', 'avatar_url'),
        }),
    )
    
    # Fields shown when creating a new user via admin
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('SkillBridge Roles', {
            'fields': ('is_talent', 'is_org_admin', 'is_mentor', 'is_school_admin'),
        }),
    )
    
    # Read-only fields
    readonly_fields = ['supabase_uid', 'created_at', 'updated_at']

