"""
Opportunity Admin Configuration
===============================
"""

from django.contrib import admin
from .models import Opportunity, Application


class ApplicationInline(admin.TabularInline):
    model = Application
    extra = 0
    readonly_fields = ['talent', 'status', 'created_at']
    can_delete = False


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['title', 'opportunity_type', 'status', 'organization', 'mentor', 'is_remote', 'is_paid', 'created_at']
    list_filter = ['opportunity_type', 'status', 'is_remote', 'is_paid']
    search_fields = ['title', 'description', 'organization__name']
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['organization', 'mentor', 'created_by']
    filter_horizontal = ['required_skills']
    readonly_fields = ['created_at', 'updated_at', 'published_at']
    date_hierarchy = 'created_at'
    inlines = [ApplicationInline]
    
    fieldsets = (
        (None, {'fields': ('title', 'slug', 'description', 'opportunity_type', 'status')}),
        ('Poster', {'fields': ('organization', 'mentor', 'created_by')}),
        ('Requirements', {'fields': ('required_skills', 'experience_level')}),
        ('Location', {'fields': ('is_remote', 'location')}),
        ('Compensation', {'fields': ('is_paid', 'compensation')}),
        ('Details', {'fields': ('duration', 'spots_available', 'max_applicants')}),
        ('Dates', {'fields': ('application_deadline', 'start_date', 'published_at')}),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['talent', 'opportunity', 'status', 'created_at', 'reviewed_at']
    list_filter = ['status', 'created_at']
    search_fields = ['talent__user__email', 'opportunity__title']
    autocomplete_fields = ['opportunity', 'talent', 'reviewed_by']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        (None, {'fields': ('opportunity', 'talent')}),
        ('Application', {'fields': ('cover_letter', 'resume_url')}),
        ('Status', {'fields': ('status', 'reviewer_notes', 'reviewed_by', 'reviewed_at')}),
    )

