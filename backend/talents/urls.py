"""
Talent URL Routes for SkillBridge API
=====================================

All routes prefixed with /api/v1/talents/ (configured in config/urls.py)
"""

from django.urls import path
from .views import (
    TalentDetailView,
    TalentListView,
    TalentProfileMeView,
    TalentSkillManageView,
    TalentSkillUpdateView,
)
# Talent-side mentorship views live in the mentors app (shared domain).
from mentors.mentorship_views import (
    TalentActivityDetailView,
    TalentActivityListCreateView,
    TalentMentorshipDetailView,
    TalentMentorshipListView,
    TalentSessionListView,
)
from .ai_views import (
    GenerateBioView,
    GenerateCoverLetterView,
    GenerateInterviewPrepView,
    GenerateResumeSummaryView,
)

app_name = 'talents'

urlpatterns = [
    # ── Talent Profile ──────────────────────────────────────────────────────
    path('', TalentListView.as_view(), name='list'),
    path('me/', TalentProfileMeView.as_view(), name='profile-me'),
    path('<int:talent_id>/', TalentDetailView.as_view(), name='profile-detail'),

    # ── Talent Skills ───────────────────────────────────────────────────────
    path('me/skills/', TalentSkillManageView.as_view(), name='skills-add'),
    path('me/skills/<int:skill_id>/', TalentSkillManageView.as_view(), name='skills-manage'),
    path('me/skills/<int:skill_id>/update/', TalentSkillUpdateView.as_view(), name='skills-update'),

    # ── Talent AI Features ──────────────────────────────────────────────────
    path('me/ai/bio/', GenerateBioView.as_view(), name='ai-bio'),
    path('me/ai/cover-letter/', GenerateCoverLetterView.as_view(), name='ai-cover-letter'),
    path('me/ai/interview-prep/', GenerateInterviewPrepView.as_view(), name='ai-interview-prep'),
    path('me/ai/resume/', GenerateResumeSummaryView.as_view(), name='ai-resume'),

    # ── Mentorships (talent side, read-only) ────────────────────────────────
    path('me/mentorships/',
         TalentMentorshipListView.as_view(), name='mentorship-list'),
    path('me/mentorships/<int:mentorship_id>/',
         TalentMentorshipDetailView.as_view(), name='mentorship-detail'),

    # ── Sessions (talent side, read-only, private_notes hidden) ─────────────
    path('me/mentorships/<int:mentorship_id>/sessions/',
         TalentSessionListView.as_view(), name='session-list'),

    # ── Activities (talent side, full CRUD) ─────────────────────────────────
    path('me/mentorships/<int:mentorship_id>/activities/',
         TalentActivityListCreateView.as_view(), name='activity-list-create'),
    path('me/activities/<int:activity_id>/',
         TalentActivityDetailView.as_view(), name='activity-detail'),
]
