"""
Organization Serializers for SkillBridge API
=============================================

Serializers for Organizations and membership.
"""

from rest_framework import serializers
from .models import Organization, OrganizationMember
from core.serializers import CanonicalIndustryMinimalSerializer


class OrganizationMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for organization membership.
    """
    
    user_email = serializers.CharField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.full_name', read_only=True)
    
    class Meta:
        model = OrganizationMember
        fields = [
            'id',
            'user',
            'user_email',
            'user_name',
            'role',
            'joined_at',
        ]
        read_only_fields = ['id', 'joined_at']


class OrganizationSerializer(serializers.ModelSerializer):
    """
    Full Organization serializer with nested industry.
    
    Used for:
    - GET /api/v1/organizations/me/
    - Organization details in opportunity listings
    """
    
    # Nested industry details (read-only)
    industry = CanonicalIndustryMinimalSerializer(read_only=True)
    
    # For write operations - accept industry_id
    industry_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    
    # Member count for display
    member_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Organization
        fields = [
            'id',
            'name',
            'slug',
            'description',
            'logo_url',
            'website_url',
            'industry',
            'industry_id',
            'company_size',
            'city',
            'state',
            'country',
            'is_verified',
            'member_count',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'slug', 'is_verified', 'member_count', 'created_at', 'updated_at']
    
    def get_member_count(self, obj):
        return obj.members.count()
    
    def update(self, instance, validated_data):
        """Handle industry_id update."""
        industry_id = validated_data.pop('industry_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if industry_id is not None:
            from core.models import CanonicalIndustry
            try:
                industry = CanonicalIndustry.objects.get(id=industry_id, is_active=True)
                instance.industry = industry
            except CanonicalIndustry.DoesNotExist:
                pass  # Keep existing industry if new one not found
        
        instance.save()
        return instance


class OrganizationUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating organization.
    
    PATCH /api/v1/organizations/me/
    """
    
    industry_id = serializers.IntegerField(required=False, allow_null=True)
    
    class Meta:
        model = Organization
        fields = [
            'name',
            'description',
            'logo_url',
            'website_url',
            'industry_id',
            'company_size',
            'city',
            'state',
            'country',
        ]
    
    def update(self, instance, validated_data):
        """Handle industry_id update."""
        industry_id = validated_data.pop('industry_id', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if industry_id is not None:
            from core.models import CanonicalIndustry
            try:
                industry = CanonicalIndustry.objects.get(id=industry_id, is_active=True)
                instance.industry = industry
            except CanonicalIndustry.DoesNotExist:
                pass
        
        instance.save()
        return instance


class OrganizationMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal organization serializer for embedding.
    """
    
    class Meta:
        model = Organization
        fields = ['id', 'name', 'logo_url', 'is_verified']
