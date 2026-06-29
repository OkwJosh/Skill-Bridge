"""
School Serializers for SkillBridge API
======================================

Serializers for Schools and Student Roster Records.
"""

from rest_framework import serializers
from .models import School, StudentRosterRecord


class SchoolSerializer(serializers.ModelSerializer):
    """
    Full School serializer.
    
    Used for:
    - GET /api/v1/schools/me/
    """
    
    admin_count = serializers.SerializerMethodField()
    roster_count = serializers.SerializerMethodField()
    verified_students_count = serializers.SerializerMethodField()
    
    class Meta:
        model = School
        fields = [
            'id',
            'name',
            'slug',
            'school_type',
            'website_url',
            'contact_email',
            'city',
            'state',
            'country',
            'is_verified',
            'admin_count',
            'roster_count',
            'verified_students_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'slug', 'is_verified', 'admin_count',
            'roster_count', 'verified_students_count',
            'created_at', 'updated_at'
        ]
    
    def get_admin_count(self, obj):
        return obj.admins.count()
    
    def get_roster_count(self, obj):
        return obj.roster_records.count()
    
    def get_verified_students_count(self, obj):
        return obj.roster_records.filter(has_consented=True).count()


class StudentRosterRecordSerializer(serializers.ModelSerializer):
    """
    Serializer for student roster records.
    
    Used by school admins to view/manage roster.
    """
    
    school_name = serializers.CharField(source='school.name', read_only=True)
    talent_email = serializers.CharField(source='talent_profile.user.email', read_only=True, default=None)
    
    class Meta:
        model = StudentRosterRecord
        fields = [
            'id',
            'school',
            'school_name',
            'matriculation_number',
            'email',
            'full_name',
            'department',
            'course_of_study',
            'enrollment_year',
            'expected_graduation_year',
            'graduation_year',
            'is_graduated',
            'cgpa',
            'has_consented',
            'consented_at',
            'talent_profile',
            'talent_email',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'has_consented', 'consented_at',
            'talent_profile', 'created_at', 'updated_at'
        ]


class StudentRosterUploadSerializer(serializers.Serializer):
    """
    Serializer for uploading student roster records.

    POST /api/v1/schools/me/roster/
    """

    matriculation_number = serializers.CharField(max_length=50)
    email = serializers.EmailField(required=False, allow_blank=True)
    full_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    department = serializers.CharField(max_length=200, required=False, allow_blank=True)
    course_of_study = serializers.CharField(max_length=200, required=False, allow_blank=True)
    enrollment_year = serializers.IntegerField(required=False, allow_null=True)
    expected_graduation_year = serializers.IntegerField(required=False, allow_null=True)
    graduation_year = serializers.IntegerField(required=False, allow_null=True)
    is_graduated = serializers.BooleanField(default=False)
    cgpa = serializers.DecimalField(max_digits=3, decimal_places=2, required=False, allow_null=True)


class SchoolCreateSerializer(serializers.ModelSerializer):
    """POST /api/v1/schools/ — first-time setup for a school admin."""

    class Meta:
        model = School
        fields = [
            'name', 'school_type', 'website_url', 'contact_email',
            'city', 'state', 'country',
        ]

    def validate_name(self, value):
        if not value or not value.strip():
            raise serializers.ValidationError('School name is required.')
        return value.strip()


class RosterCSVUploadSerializer(serializers.Serializer):
    """
    POST /api/v1/schools/me/roster/import/  (multipart/form-data)

    Expected CSV columns (header row required, case-insensitive):
      matriculation_number (required)
      email, full_name, department, course_of_study,
      enrollment_year, expected_graduation_year, graduation_year,
      is_graduated, cgpa
    """
    file = serializers.FileField()

    def validate_file(self, value):
        # Best-effort guard: most browsers send `text/csv`, but some send
        # `application/vnd.ms-excel` or `application/octet-stream`. We accept
        # by extension as the primary signal.
        name = (getattr(value, 'name', '') or '').lower()
        if not name.endswith('.csv'):
            raise serializers.ValidationError('Please upload a .csv file.')
        if value.size > 5 * 1024 * 1024:
            raise serializers.ValidationError('CSV must be ≤ 5MB.')
        return value


class ConsentSerializer(serializers.Serializer):
    """
    Serializer for talent consent to school data.
    
    POST /api/v1/schools/consent/
    
    Talent provides their matriculation number to link with school records.
    """
    
    matriculation_number = serializers.CharField(
        max_length=50,
        help_text="Your matriculation/registration number"
    )
    
    school_id = serializers.IntegerField(
        required=False,
        help_text="Optional: Specific school ID if you know it"
    )
