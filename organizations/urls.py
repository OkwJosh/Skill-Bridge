"""
Organization URL Routes for SkillBridge API
===========================================

All routes prefixed with /api/v1/organizations/ (configured in config/urls.py)
"""

from django.urls import path
from .views import OrganizationMeView, TalentSearchView

app_name = 'organizations'

urlpatterns = [
    # Organization Profile
    # GET  /api/v1/organizations/me/ - Get current user's organization
    # PATCH /api/v1/organizations/me/ - Update organization
    path('me/', OrganizationMeView.as_view(), name='org-me'),
    
    # Talent Search (Proactive Sourcing)
    # GET /api/v1/organizations/me/talent-search/ - Search available talents
    path('me/talent-search/', TalentSearchView.as_view(), name='talent-search'),
]
