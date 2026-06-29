"""
School Admin Configuration
==========================
"""

from django.contrib import admin
from .models import School, StudentRosterRecord


class StudentRosterInline(admin.TabularInline):
    model = StudentRosterRecord
    extra = 0
    readonly_fields = ['has_consented', 'consented_at', 'talent_profile']
    fields = ['matriculation_number', 'full_name', 'department', 'has_consented', 'talent_profile']


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ['name', 'school_type', 'state', 'is_verified', 'created_at']
    list_filter = ['school_type', 'is_verified', 'state']
    search_fields = ['name', 'city', 'state']
    prepopulated_fields = {'slug': ('name',)}
    filter_horizontal = ['admins']
    inlines = [StudentRosterInline]
    
    fieldsets = (
        (None, {'fields': ('name', 'slug', 'school_type')}),
        ('Contact', {'fields': ('website_url', 'contact_email')}),
        ('Location', {'fields': ('city', 'state', 'country')}),
        ('Status', {'fields': ('is_verified',)}),
        ('Admins', {'fields': ('admins',)}),
    )


@admin.register(StudentRosterRecord)
class StudentRosterRecordAdmin(admin.ModelAdmin):
    list_display = ['matriculation_number', 'school', 'full_name', 'department', 'has_consented', 'talent_profile']
    list_filter = ['school', 'has_consented', 'is_graduated']
    search_fields = ['matriculation_number', 'full_name', 'email']
    autocomplete_fields = ['school', 'talent_profile']
    readonly_fields = ['has_consented', 'consented_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('School', {'fields': ('school',)}),
        ('Student Info', {'fields': ('matriculation_number', 'email', 'full_name')}),
        ('Academic', {'fields': ('department', 'course_of_study', 'enrollment_year', 'expected_graduation_year', 'graduation_year', 'is_graduated', 'cgpa')}),
        ('Consent', {'fields': ('has_consented', 'consented_at', 'talent_profile')}),
    )

