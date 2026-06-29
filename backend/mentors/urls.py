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
from .mentorship_views import (
    MentorActivityListView,
    MentorMentorshipDetailView,
    MentorMentorshipListCreateView,
    MentorSessionDetailView,
    MentorSessionListCreateView,
)

app_name = 'mentors'

urlpatterns = [
    # ── Mentor Profile ──────────────────────────────────────────────────────
    path('me/', MentorMeView.as_view(), name='profile-me'),

    # ── Endorsements ────────────────────────────────────────────────────────
    path('me/endorsements/', MentorEndorsementCreateView.as_view(), name='endorsement-create'),
    path('me/endorsements/list/', MentorEndorsementListView.as_view(), name='endorsement-list'),

    # ── Mentorships (mentor side) ───────────────────────────────────────────
    # GET   list      / POST  create
    path('me/mentorships/',
         MentorMentorshipListCreateView.as_view(), name='mentorship-list-create'),
    # GET   detail    / PATCH update
    path('me/mentorships/<int:mentorship_id>/',
         MentorMentorshipDetailView.as_view(), name='mentorship-detail'),

    # ── Sessions (mentor side) ──────────────────────────────────────────────
    path('me/mentorships/<int:mentorship_id>/sessions/',
         MentorSessionListCreateView.as_view(), name='session-list-create'),
    path('me/sessions/<int:session_id>/',
         MentorSessionDetailView.as_view(), name='session-detail'),

    # ── Mentee activities (mentor read-only) ────────────────────────────────
    path('me/mentorships/<int:mentorship_id>/activities/',
         MentorActivityListView.as_view(), name='mentor-activity-list'),
]
