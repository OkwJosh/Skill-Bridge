"""
Mentor Admin Configuration
==========================
"""

from django.contrib import admin
from .models import MentorProfile


@admin.register(MentorProfile)
class MentorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'headline', 'is_verified', 'is_accepting_mentees', 'endorsements_given', 'created_at']
    list_filter = ['is_verified', 'is_accepting_mentees']
    search_fields = ['user__email', 'user__full_name', 'headline', 'bio']
    autocomplete_fields = ['user']
    filter_horizontal = ['expertise_areas']
    readonly_fields = ['endorsements_given', 'created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('user',)}),
        ('Profile', {'fields': ('headline', 'bio', 'expertise_areas')}),
        ('Links', {'fields': ('linkedin_url', 'website_url')}),
        ('Availability', {'fields': ('is_accepting_mentees', 'max_mentees')}),
        ('Status', {'fields': ('is_verified', 'endorsements_given')}),
    )

