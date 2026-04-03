"""
Organization Filters for SkillBridge API
========================================

Django Filter classes for advanced querying.
"""

import django_filters
from talents.models import TalentProfile, EducationRoute


class TalentSearchFilter(django_filters.FilterSet):
    """
    Filter for proactive talent sourcing.
    
    Allows organizations to search talents by:
    - Skills (by CanonicalSkill IDs)
    - Education route
    - School verification status
    - Availability
    - Location
    """
    
    # Filter by skill IDs (comma-separated or multiple params)
    # Example: ?skills=1,2,3 or ?skills=1&skills=2&skills=3
    skills = django_filters.BaseInFilter(
        field_name='skills__skill_id',
        label='Skill IDs (comma-separated)',
    )
    
    # Filter by education route
    education_route = django_filters.ChoiceFilter(
        choices=EducationRoute.choices,
        label='Education Route',
    )
    
    # Filter by school verification
    is_school_verified = django_filters.BooleanFilter(
        label='School Verified',
    )
    
    # Filter by availability
    is_available = django_filters.BooleanFilter(
        label='Currently Available',
    )
    
    # Filter by location
    city = django_filters.CharFilter(
        lookup_expr='icontains',
        label='City (partial match)',
    )
    
    state = django_filters.CharFilter(
        lookup_expr='icontains',
        label='State (partial match)',
    )
    
    country = django_filters.CharFilter(
        lookup_expr='iexact',
        label='Country (exact match)',
    )
    
    # Filter by proficiency in any skill
    min_proficiency = django_filters.ChoiceFilter(
        field_name='skills__proficiency',
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        label='Minimum Proficiency',
    )
    
    # Filter for endorsed skills only
    has_endorsed_skills = django_filters.BooleanFilter(
        field_name='skills__is_endorsed',
        label='Has Endorsed Skills',
    )
    
    class Meta:
        model = TalentProfile
        fields = [
            'skills',
            'education_route',
            'is_school_verified',
            'is_available',
            'city',
            'state',
            'country',
        ]
