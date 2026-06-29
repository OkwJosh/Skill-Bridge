"""
Core/Taxonomy Admin Configuration
=================================

Admin interface for canonical Skills and Industries.
"""

from django.contrib import admin
from .models import CanonicalSkill, CanonicalIndustry


@admin.register(CanonicalSkill)
class CanonicalSkillAdmin(admin.ModelAdmin):
    """
    Admin for managing the canonical skills list.
    
    Features:
    - Auto-generate slug from name
    - Filter by category and active status
    - Bulk activate/deactivate actions
    """
    
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'category', 'description']
    ordering = ['category', 'name']
    
    # Auto-fill slug from name
    prepopulated_fields = {'slug': ('name',)}
    
    # Editable from list view
    list_editable = ['is_active']
    
    # Organize fields in form
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'category'),
        }),
        ('Details', {
            'fields': ('description', 'is_active'),
        }),
    )
    
    # Bulk actions
    actions = ['activate_skills', 'deactivate_skills']
    
    @admin.action(description='Activate selected skills')
    def activate_skills(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} skills activated.')
    
    @admin.action(description='Deactivate selected skills')
    def deactivate_skills(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} skills deactivated.')


@admin.register(CanonicalIndustry)
class CanonicalIndustryAdmin(admin.ModelAdmin):
    """
    Admin for managing the canonical industries list.
    """
    
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['name']
    
    # Auto-fill slug from name
    prepopulated_fields = {'slug': ('name',)}
    
    # Editable from list view
    list_editable = ['is_active']
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug'),
        }),
        ('Details', {
            'fields': ('description', 'is_active'),
        }),
    )

