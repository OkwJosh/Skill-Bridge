"""
Talents Admin Configuration
===========================

Admin interface for Talent Profiles and Skills.
"""

from django.contrib import admin
from .models import TalentProfile, TalentSkill


class TalentSkillInline(admin.TabularInline):
    """
    Inline editor for talent skills within TalentProfile admin.
    """
    model = TalentSkill
    extra = 1  # Show 1 empty row for adding
    autocomplete_fields = ['skill']  # Enable search for skills
    readonly_fields = ['endorsed_by', 'endorsed_at']
    
    fields = [
        'skill',
        'proficiency',
        'years_experience',
        'is_primary',
        'is_endorsed',
        'endorsed_by',
    ]


@admin.register(TalentProfile)
class TalentProfileAdmin(admin.ModelAdmin):
    """
    Admin for Talent Profiles.
    
    Features:
    - Inline skill management
    - Verification status tracking
    - Filter by education route and verification
    """
    
    list_display = [
        'user',
        'headline',
        'education_route',
        'is_school_verified',
        'is_available',
        'city',
        'created_at',
    ]
    
    list_filter = [
        'education_route',
        'is_school_verified',
        'is_available',
        'country',
        'created_at',
    ]
    
    search_fields = [
        'user__email',
        'user__full_name',
        'headline',
        'institution_name',
        'city',
    ]
    
    ordering = ['-created_at']
    
    # Inline skills editor
    inlines = [TalentSkillInline]
    
    # Autocomplete for user selection
    autocomplete_fields = ['user', 'verified_by']
    
    # Read-only fields
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',),
        }),
        ('Professional Info', {
            'fields': ('headline', 'bio', 'is_available'),
        }),
        ('Education', {
            'fields': (
                'education_route',
                'institution_name',
                'field_of_study',
                'graduation_year',
            ),
        }),
        ('School Verification', {
            'fields': ('is_school_verified', 'verified_by', 'verified_at'),
            'classes': ('collapse',),
        }),
        ('Location', {
            'fields': ('city', 'state', 'country'),
        }),
        ('Links', {
            'fields': ('portfolio_url', 'linkedin_url', 'github_url', 'resume_url'),
            'classes': ('collapse',),
        }),
        ('Preferences', {
            'fields': ('preferred_industries',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    
    # Filter horizontal for M2M fields
    filter_horizontal = ['preferred_industries']


@admin.register(TalentSkill)
class TalentSkillAdmin(admin.ModelAdmin):
    """
    Admin for Talent Skills (junction table).
    Useful for bulk skill management and endorsement tracking.
    """
    
    list_display = [
        'talent',
        'skill',
        'proficiency',
        'years_experience',
        'is_primary',
        'is_endorsed',
        'endorsed_by',
    ]
    
    list_filter = [
        'proficiency',
        'is_primary',
        'is_endorsed',
        'skill__category',
    ]
    
    search_fields = [
        'talent__user__email',
        'skill__name',
    ]
    
    autocomplete_fields = ['talent', 'skill', 'endorsed_by']
    
    readonly_fields = ['endorsed_at', 'created_at', 'updated_at']

