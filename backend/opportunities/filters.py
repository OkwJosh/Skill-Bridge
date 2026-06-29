"""
Opportunity Filters for SkillBridge API
=======================================

Django Filter classes for opportunity querying.
"""

import django_filters
from .models import Opportunity, OpportunityType, OpportunityStatus


class OpportunityFilter(django_filters.FilterSet):
    """
    Filter for opportunity listings.
    
    Allows filtering by:
    - opportunity_type
    - status
    - is_remote
    - is_paid
    - skills
    - organization
    """
    
    opportunity_type = django_filters.ChoiceFilter(
        choices=OpportunityType.choices,
        label='Opportunity Type'
    )
    
    status = django_filters.ChoiceFilter(
        choices=OpportunityStatus.choices,
        label='Status'
    )
    
    is_remote = django_filters.BooleanFilter(label='Remote Only')
    
    is_paid = django_filters.BooleanFilter(label='Paid Only')
    
    # Filter by required skill IDs
    skills = django_filters.BaseInFilter(
        field_name='required_skills__id',
        label='Required Skill IDs'
    )
    
    # Filter by organization
    organization = django_filters.NumberFilter(
        field_name='organization_id',
        label='Organization ID'
    )
    
    # Filter by mentor
    mentor = django_filters.NumberFilter(
        field_name='mentor_id',
        label='Mentor ID'
    )
    
    class Meta:
        model = Opportunity
        fields = [
            'opportunity_type',
            'status',
            'is_remote',
            'is_paid',
            'skills',
            'organization',
            'mentor',
        ]
