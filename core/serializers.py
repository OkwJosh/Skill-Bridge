"""
Core Serializers for SkillBridge API
====================================

Serializers for canonical taxonomy data (Skills, Industries).
These are used across multiple apps for consistent data representation.
"""

from rest_framework import serializers
from .models import CanonicalSkill, CanonicalIndustry


class CanonicalSkillSerializer(serializers.ModelSerializer):
    """
    Serializer for CanonicalSkill.
    
    Used when:
    - Listing available skills for selection
    - Embedding skills in TalentProfile responses
    - Filtering opportunities by required skills
    """
    
    class Meta:
        model = CanonicalSkill
        fields = [
            'id',
            'name',
            'slug',
            'category',
            'description',
        ]
        read_only_fields = ['id', 'slug']


class CanonicalSkillMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal skill serializer for embedding in other responses.
    Reduces payload size when full details aren't needed.
    """
    
    class Meta:
        model = CanonicalSkill
        fields = ['id', 'name', 'category']


class CanonicalIndustrySerializer(serializers.ModelSerializer):
    """
    Serializer for CanonicalIndustry.
    
    Used when:
    - Listing available industries for selection
    - Embedding industry in Organization responses
    - Filtering opportunities by industry
    """
    
    class Meta:
        model = CanonicalIndustry
        fields = [
            'id',
            'name',
            'slug',
            'description',
        ]
        read_only_fields = ['id', 'slug']


class CanonicalIndustryMinimalSerializer(serializers.ModelSerializer):
    """
    Minimal industry serializer for embedding.
    """
    
    class Meta:
        model = CanonicalIndustry
        fields = ['id', 'name']
