"""
Mentor URL Routes for SkillBridge API
=====================================

All routes prefixed with /api/v1/mentors/ (configured in config/urls.py)
"""

from django.urls import path
from .views import (
    MentorMeView,
    MentorEndorsementCreateView,
    MentorEndorsementListView,
)

app_name = 'mentors'

urlpatterns = [
    # Mentor Profile
    # GET  /api/v1/mentors/me/ - Get current user's mentor profile
    # PATCH /api/v1/mentors/me/ - Update current user's mentor profile
    path('me/', MentorMeView.as_view(), name='profile-me'),
    
    # Endorsements
    # GET  /api/v1/mentors/me/endorsements/ - List endorsements given
    # POST /api/v1/mentors/me/endorsements/ - Create new endorsement
    path('me/endorsements/', MentorEndorsementCreateView.as_view(), name='endorsement-create'),
    path('me/endorsements/list/', MentorEndorsementListView.as_view(), name='endorsement-list'),
]
