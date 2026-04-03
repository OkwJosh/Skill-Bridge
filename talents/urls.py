"""
Talent URL Routes for SkillBridge API
=====================================

All routes prefixed with /api/v1/talents/ (configured in config/urls.py)
"""

from django.urls import path
from .views import (
    TalentProfileMeView,
    TalentSkillManageView,
    TalentSkillUpdateView,
)

app_name = 'talents'

urlpatterns = [
    # Talent Profile
    # GET  /api/v1/talents/me/ - Get current user's talent profile
    # PATCH /api/v1/talents/me/ - Update current user's talent profile
    path('me/', TalentProfileMeView.as_view(), name='profile-me'),
    
    # Talent Skills
    # POST /api/v1/talents/me/skills/ - Add a skill
    path('me/skills/', TalentSkillManageView.as_view(), name='skills-add'),
    
    # DELETE /api/v1/talents/me/skills/<skill_id>/ - Remove a skill
    # PATCH /api/v1/talents/me/skills/<skill_id>/ - Update skill details
    path('me/skills/<int:skill_id>/', TalentSkillManageView.as_view(), name='skills-manage'),
    path('me/skills/<int:skill_id>/update/', TalentSkillUpdateView.as_view(), name='skills-update'),
]
