"""
Organization Admin Configuration
================================

Admin interface for Organizations and Members.
"""

from django.contrib import admin
from .models import Organization, OrganizationMember


class OrganizationMemberInline(admin.TabularInline):
    """Inline editor for organization members."""
    model = OrganizationMember
    extra = 1
    autocomplete_fields = ['user']


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Admin for Organizations."""
    
    list_display = ['name', 'industry', 'company_size', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'industry', 'company_size', 'country']
    search_fields = ['name', 'description', 'city']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['name']
    
    inlines = [OrganizationMemberInline]
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'description', 'logo_url', 'website_url'),
        }),
        ('Classification', {
            'fields': ('industry', 'company_size'),
        }),
        ('Location', {
            'fields': ('city', 'state', 'country'),
        }),
        ('Status', {
            'fields': ('is_verified',),
        }),
    )


@admin.register(OrganizationMember)
class OrganizationMemberAdmin(admin.ModelAdmin):
    """Admin for Organization Members."""
    
    list_display = ['user', 'organization', 'role', 'joined_at']
    list_filter = ['role', 'organization']
    search_fields = ['user__email', 'organization__name']
    autocomplete_fields = ['user', 'organization']

