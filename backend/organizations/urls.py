"""
Organization URL Routes for SkillBridge API
===========================================

All routes prefixed with /api/v1/organizations/ (configured in config/urls.py)
"""

from django.urls import path
from .views import OrganizationCreateView, OrganizationMeView, TalentSearchView

app_name = 'organizations'

urlpatterns = [
    # POST /api/v1/organizations/ — first-time setup
    path('', OrganizationCreateView.as_view(), name='org-create'),

    # GET / PATCH /api/v1/organizations/me/
    path('me/', OrganizationMeView.as_view(), name='org-me'),

    # GET /api/v1/organizations/me/talent-search/ — org-only deep search
    path('me/talent-search/', TalentSearchView.as_view(), name='talent-search'),
]
