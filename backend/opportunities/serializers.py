"""
Opportunity Serializers for SkillBridge API
===========================================

Serializers for Opportunities and Applications.
"""

from rest_framework import serializers
from django.utils import timezone
from django.utils.text import slugify
import uuid

from .models import (
    Opportunity, Application, OpportunityType, OpportunityStatus, ApplicationStatus,
    SavedOpportunity, ApplicationInterview
)
from core.serializers import CanonicalSkillMinimalSerializer
from organizations.serializers import OrganizationMinimalSerializer


class OpportunityMentorSerializer(serializers.Serializer):
    """Embedded mentor info for opportunities."""
    
    id = serializers.IntegerField(read_only=True)
    user_id = serializers.IntegerField(source='user.id', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    headline = serializers.CharField(read_only=True)


class OpportunitySerializer(serializers.ModelSerializer):
    """
    Full Opportunity serializer.
    
    Used for:
    - GET /api/v1/opportunities/
    - GET /api/v1/opportunities/<pk>/
    """
    
    # Nested relationships (read-only)
    organization = OrganizationMinimalSerializer(read_only=True)
    mentor = OpportunityMentorSerializer(read_only=True)
    required_skills = CanonicalSkillMinimalSerializer(many=True, read_only=True)
    poster_name = serializers.CharField(read_only=True)
    
    # For write operations
    required_skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    # Computed fields
    application_count = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    
    class Meta:
        model = Opportunity
        fields = [
            'id',
            'title',
            'slug',
            'description',
            'opportunity_type',
            'status',
            'organization',
            'mentor',
            'poster_name',
            'category',
            'required_skills',
            'required_skill_ids',
            'experience_level',
            'is_remote',
            'location',
            'is_paid',
            'compensation',
            'duration',
            'max_applicants',
            'spots_available',
            'application_deadline',
            'start_date',
            'application_count',
            'is_saved',
            'created_at',
            'updated_at',
            'published_at',
        ]
        read_only_fields = [
            'id', 'slug', 'organization', 'mentor', 'poster_name',
            'application_count', 'is_saved', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_application_count(self, obj):
        return obj.applications.count()

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            annotated = getattr(obj, 'is_saved_by_user', None)
            if annotated is not None:
                return annotated
            return SavedOpportunity.objects.filter(user=request.user, opportunity=obj).exists()
        return False


class OpportunityCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating opportunities.
    
    POST /api/v1/opportunities/
    """
    
    required_skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        default=[]
    )
    
    class Meta:
        model = Opportunity
        fields = [
            'title',
            'description',
            'opportunity_type',
            'required_skill_ids',
            'experience_level',
            'is_remote',
            'location',
            'is_paid',
            'compensation',
            'duration',
            'max_applicants',
            'spots_available',
            'application_deadline',
            'start_date',
        ]
    
    def create(self, validated_data):
        """Create opportunity with auto-generated slug."""
        skill_ids = validated_data.pop('required_skill_ids', [])
        
        # Generate unique slug
        base_slug = slugify(validated_data['title'])
        slug = f"{base_slug}-{uuid.uuid4().hex[:8]}"
        validated_data['slug'] = slug
        
        # Set status to open and published_at
        validated_data['status'] = OpportunityStatus.OPEN
        validated_data['published_at'] = timezone.now()
        
        opportunity = Opportunity.objects.create(**validated_data)
        
        # Set required skills
        if skill_ids:
            from core.models import CanonicalSkill
            skills = CanonicalSkill.objects.filter(id__in=skill_ids, is_active=True)
            opportunity.required_skills.set(skills)
        
        return opportunity


class OpportunityUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating opportunities.
    
    PATCH /api/v1/opportunities/<pk>/
    """
    
    required_skill_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = Opportunity
        fields = [
            'title',
            'description',
            'opportunity_type',
            'status',
            'required_skill_ids',
            'experience_level',
            'is_remote',
            'location',
            'is_paid',
            'compensation',
            'duration',
            'max_applicants',
            'spots_available',
            'application_deadline',
            'start_date',
        ]
    
    def update(self, instance, validated_data):
        skill_ids = validated_data.pop('required_skill_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if skill_ids is not None:
            from core.models import CanonicalSkill
            skills = CanonicalSkill.objects.filter(id__in=skill_ids, is_active=True)
            instance.required_skills.set(skills)
        
        return instance


class OpportunityListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for opportunity listings.
    """

    organization = OrganizationMinimalSerializer(read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True, default=None)
    mentor_name = serializers.CharField(source='mentor.user.full_name', read_only=True, default=None)
    poster_name = serializers.CharField(read_only=True)
    required_skills = CanonicalSkillMinimalSerializer(many=True, read_only=True)
    # Read from the queryset annotation when present (avoids N+1); falls back to
    # a direct count for un-annotated callers.
    application_count = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    class Meta:
        model = Opportunity
        fields = [
            'id',
            'title',
            'slug',
            'opportunity_type',
            'status',
            'organization',
            'organization_name',
            'mentor_name',
            'poster_name',
            'category',
            'required_skills',
            'is_remote',
            'location',
            'is_paid',
            'compensation',
            'duration',
            'application_deadline',
            'application_count',
            'is_saved',
            'created_at',
        ]

    def get_application_count(self, obj):
        annotated = getattr(obj, 'application_count', None)
        return annotated if annotated is not None else obj.applications.count()

    def get_is_saved(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            annotated = getattr(obj, 'is_saved_by_user', None)
            if annotated is not None:
                return annotated
            return SavedOpportunity.objects.filter(user=request.user, opportunity=obj).exists()
        return False


# =============================================================================
# Application Serializers
# =============================================================================

class ApplicationTalentSerializer(serializers.Serializer):
    """Embedded talent info for applications."""
    
    id = serializers.IntegerField(read_only=True)
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    headline = serializers.CharField(read_only=True)
    is_school_verified = serializers.BooleanField(read_only=True)


class OpportunitySummarySerializer(serializers.ModelSerializer):
    """
    Compact opportunity view embedded inside an Application so the
    talent's "My Applications" list can render real details (title,
    poster, type, location) without a second round-trip per row.
    """

    organization_name = serializers.CharField(source='organization.name', read_only=True, default=None)
    poster_name = serializers.CharField(read_only=True)

    class Meta:
        model = Opportunity
        fields = [
            'id',
            'title',
            'slug',
            'opportunity_type',
            'status',
            'organization_name',
            'poster_name',
            'location',
            'is_remote',
            'is_paid',
            'compensation',
            'duration',
            'application_deadline',
        ]
        read_only_fields = fields


class ApplicationSerializer(serializers.ModelSerializer):
    """
    Full Application serializer.

    `opportunity` is nested (read-only) so consumers get the opportunity's
    title/poster/type inline. `opportunity_title` is kept as a flat alias
    for backwards-compatibility with any caller that still reads it.
    """

    talent = ApplicationTalentSerializer(read_only=True)
    opportunity = OpportunitySummarySerializer(read_only=True)
    opportunity_title = serializers.CharField(source='opportunity.title', read_only=True)
    interviews = serializers.SerializerMethodField()

    class Meta:
        model = Application
        fields = [
            'id',
            'opportunity',
            'opportunity_title',
            'talent',
            'cover_letter',
            'resume_url',
            'status',
            'reviewer_notes',
            'reviewed_by',
            'reviewed_at',
            'interviews',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'opportunity', 'talent', 'reviewer_notes',
            'reviewed_by', 'reviewed_at', 'interviews', 'created_at', 'updated_at'
        ]

    def get_interviews(self, obj):
        return ApplicationInterviewSerializer(obj.interviews.all(), many=True).data


class ApplicationCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating an application.
    
    POST /api/v1/opportunities/<opportunity_id>/apply/
    """
    
    class Meta:
        model = Application
        fields = [
            'cover_letter',
            'resume_url',
        ]


class ApplicationStatusUpdateSerializer(serializers.Serializer):
    """
    Serializer for updating application status.
    
    PATCH /api/v1/opportunities/applications/<pk>/status/
    """
    
    status = serializers.ChoiceField(choices=ApplicationStatus.choices)
    reviewer_notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_status(self, value):
        """Validate status transition."""
        current_status = self.instance.status if self.instance else None
        
        # Don't allow changing from terminal states
        terminal_states = [ApplicationStatus.ACCEPTED, ApplicationStatus.REJECTED, ApplicationStatus.WITHDRAWN]
        if current_status in terminal_states:
            raise serializers.ValidationError(
                f"Cannot change status from '{current_status}'. Application is in a terminal state."
            )
        
        return value

class ApplicationInterviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationInterview
        fields = [
            'id',
            'application',
            'round_name',
            'scheduled_at',
            'meeting_link',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'application', 'created_at', 'updated_at']
