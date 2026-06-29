"""
Talent Serializers for SkillBridge API
======================================

Modular serializers for TalentProfile and TalentSkill.
Follows the principle: "No Monolithic Serializers"
"""

from rest_framework import serializers
from .models import TalentProfile, TalentSkill, EducationRoute
from core.serializers import CanonicalSkillMinimalSerializer, CanonicalIndustryMinimalSerializer


class TalentSkillSerializer(serializers.ModelSerializer):
    """
    Serializer for TalentSkill junction table.
    
    Includes nested skill details for read operations.
    """
    
    # Nested skill details (read-only)
    skill = CanonicalSkillMinimalSerializer(read_only=True)
    
    # For write operations - accept skill_id
    skill_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = TalentSkill
        fields = [
            'id',
            'skill',
            'skill_id',
            'proficiency',
            'years_experience',
            'is_primary',
            'is_endorsed',
            'endorsed_by',
            'endorsed_at',
        ]
        read_only_fields = ['id', 'is_endorsed', 'endorsed_by', 'endorsed_at']


class TalentSkillCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for adding a skill to a talent profile.
    
    POST /api/v1/talents/me/skills/
    """
    
    skill_id = serializers.IntegerField()
    
    class Meta:
        model = TalentSkill
        fields = [
            'skill_id',
            'proficiency',
            'years_experience',
            'is_primary',
        ]
    
    def validate_skill_id(self, value):
        """Ensure the skill exists and is active."""
        from core.models import CanonicalSkill
        
        try:
            skill = CanonicalSkill.objects.get(id=value, is_active=True)
        except CanonicalSkill.DoesNotExist:
            raise serializers.ValidationError("Skill not found or inactive.")
        return value
    
    def validate(self, attrs):
        """Check for duplicate skill."""
        talent = self.context.get('talent')
        skill_id = attrs.get('skill_id')
        
        if talent and TalentSkill.objects.filter(talent=talent, skill_id=skill_id).exists():
            raise serializers.ValidationError({
                'skill_id': 'You already have this skill in your profile.'
            })
        return attrs


class TalentUserSerializer(serializers.Serializer):
    """
    Embedded user info for TalentProfile responses.
    Avoids circular imports by not using UserSerializer.
    """
    
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(read_only=True)
    full_name = serializers.CharField(read_only=True)
    avatar_url = serializers.URLField(read_only=True)


class TalentProfileSerializer(serializers.ModelSerializer):
    """
    Full TalentProfile serializer with nested user and skills.
    
    Used for:
    - GET /api/v1/talents/me/
    - Talent search results
    """
    
    # Nested user info (read-only)
    user = TalentUserSerializer(read_only=True)
    
    # Nested skills list
    skills = TalentSkillSerializer(many=True, read_only=True)
    
    # Nested preferred industries
    preferred_industries = CanonicalIndustryMinimalSerializer(many=True, read_only=True)
    
    # Computed location property
    location = serializers.CharField(read_only=True)
    
    # For write operations - accept industry IDs
    preferred_industry_ids = serializers.ListField(
        child=serializers.IntegerField(),
        write_only=True,
        required=False
    )
    
    class Meta:
        model = TalentProfile
        fields = [
            # Identity
            'id',
            'user',
            
            # Professional
            'headline',
            'bio',
            
            # Education
            'education_route',
            'institution_name',
            'field_of_study',
            'graduation_year',
            
            # Verification
            'is_school_verified',
            'verified_at',
            
            # Location
            'city',
            'state',
            'country',
            'location',
            
            # Links
            'portfolio_url',
            'linkedin_url',
            'github_url',
            'resume_url',
            
            # Preferences
            'is_available',
            'preferred_industries',
            'preferred_industry_ids',
            
            # Skills
            'skills',
            
            # Timestamps
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'is_school_verified',
            'verified_at',
            'skills',
            'location',
            'created_at',
            'updated_at',
        ]
    
    def update(self, instance, validated_data):
        """Handle M2M preferred_industries update."""
        industry_ids = validated_data.pop('preferred_industry_ids', None)
        
        # Update scalar fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update M2M if provided
        if industry_ids is not None:
            from core.models import CanonicalIndustry
            industries = CanonicalIndustry.objects.filter(
                id__in=industry_ids,
                is_active=True
            )
            instance.preferred_industries.set(industries)
        
        return instance


class TalentProfileUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating talent profile.
    
    PATCH /api/v1/talents/me/
    """
    
    preferred_industry_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False
    )
    
    class Meta:
        model = TalentProfile
        fields = [
            'headline',
            'bio',
            'education_route',
            'institution_name',
            'field_of_study',
            'graduation_year',
            'city',
            'state',
            'country',
            'portfolio_url',
            'linkedin_url',
            'github_url',
            'resume_url',
            'is_available',
            'preferred_industry_ids',
        ]
    
    def update(self, instance, validated_data):
        """Handle M2M preferred_industries update."""
        industry_ids = validated_data.pop('preferred_industry_ids', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if industry_ids is not None:
            from core.models import CanonicalIndustry
            industries = CanonicalIndustry.objects.filter(
                id__in=industry_ids,
                is_active=True
            )
            instance.preferred_industries.set(industries)
        
        return instance


class TalentSearchSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for talent search results.
    
    Used in: GET /api/v1/organizations/me/talent-search/
    """
    
    user = TalentUserSerializer(read_only=True)
    skills = TalentSkillSerializer(many=True, read_only=True)
    location = serializers.CharField(read_only=True)
    
    class Meta:
        model = TalentProfile
        fields = [
            'id',
            'user',
            'headline',
            'education_route',
            'is_school_verified',
            'location',
            'is_available',
            'skills',
        ]
