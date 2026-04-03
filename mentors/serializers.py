"""
Mentor Serializers for SkillBridge API
======================================

Serializers for MentorProfile and skill endorsements.
"""

from rest_framework import serializers
from django.utils import timezone

from .models import MentorProfile
from talents.models import TalentSkill, TalentProfile
from core.serializers import CanonicalSkillMinimalSerializer


class MentorUserSerializer(serializers.Serializer):
    """Embedded user info for MentorProfile responses."""
    
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    avatar_url = serializers.URLField(read_only=True)


class MentorProfileSerializer(serializers.ModelSerializer):
    """
    Full MentorProfile serializer.
    
    Used for:
    - GET /api/v1/mentors/me/
    - Mentor details in opportunities
    """
    
    user = MentorUserSerializer(read_only=True)
    expertise_areas = CanonicalSkillMinimalSerializer(many=True, read_only=True)
    
    # For write operations
    expertise_area_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = MentorProfile
        fields = [
            'id',
            'user',
            'headline',
            'bio',
            'expertise_areas',
            'expertise_area_ids',
            'linkedin_url',
            'website_url',
            'is_accepting_mentees',
            'max_mentees',
            'is_verified',
            'endorsements_given',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 'user', 'is_verified', 'endorsements_given',
            'created_at', 'updated_at'
        ]
    
    def update(self, instance, validated_data):
        """Handle M2M expertise_areas update."""
        expertise_ids = validated_data.pop('expertise_area_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if expertise_ids is not None:
            from core.models import CanonicalSkill
            skills = CanonicalSkill.objects.filter(id__in=expertise_ids, is_active=True)
            instance.expertise_areas.set(skills)
        
        return instance


class MentorProfileUpdateSerializer(serializers.ModelSerializer):
    """Serializer for updating mentor profile."""
    
    expertise_area_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = MentorProfile
        fields = [
            'headline',
            'bio',
            'expertise_area_ids',
            'linkedin_url',
            'website_url',
            'is_accepting_mentees',
            'max_mentees',
        ]


class EndorsementCreateSerializer(serializers.Serializer):
    """
    Serializer for creating a skill endorsement.
    
    POST /api/v1/mentors/me/endorsements/
    
    Allows a mentor to endorse a talent's skill.
    """
    
    talent_profile_id = serializers.IntegerField(
        help_text="ID of the TalentProfile to endorse"
    )
    
    skill_id = serializers.IntegerField(
        help_text="ID of the CanonicalSkill to endorse"
    )
    
    endorsement_note = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Optional note about the endorsement"
    )
    
    def validate_talent_profile_id(self, value):
        """Ensure talent profile exists."""
        try:
            TalentProfile.objects.get(id=value)
        except TalentProfile.DoesNotExist:
            raise serializers.ValidationError("Talent profile not found.")
        return value
    
    def validate(self, attrs):
        """
        Validate:
        1. Talent has this skill
        2. Skill is not already endorsed
        3. Mentor has expertise in this skill (optional but recommended)
        """
        talent_profile_id = attrs.get('talent_profile_id')
        skill_id = attrs.get('skill_id')
        
        # Check if talent has this skill
        talent_skill = TalentSkill.objects.filter(
            talent_id=talent_profile_id,
            skill_id=skill_id
        ).first()
        
        if not talent_skill:
            raise serializers.ValidationError({
                'skill_id': "Talent does not have this skill in their profile."
            })
        
        if talent_skill.is_endorsed:
            raise serializers.ValidationError({
                'skill_id': "This skill is already endorsed."
            })
        
        attrs['talent_skill'] = talent_skill
        return attrs


class EndorsementResponseSerializer(serializers.ModelSerializer):
    """
    Serializer for endorsement responses.
    Shows the endorsed skill details.
    """
    
    skill = CanonicalSkillMinimalSerializer(read_only=True)
    talent_email = serializers.CharField(source='talent.user.email', read_only=True)
    endorsed_by_name = serializers.CharField(source='endorsed_by.full_name', read_only=True)
    
    class Meta:
        model = TalentSkill
        fields = [
            'id',
            'talent_email',
            'skill',
            'proficiency',
            'is_endorsed',
            'endorsed_by',
            'endorsed_by_name',
            'endorsed_at',
            'endorsement_note',
        ]
