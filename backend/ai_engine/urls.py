from django.urls import path

from .views import (
    CurriculumAlignmentView,
    MatchCVView,
    MenteeProgressInsightView,
    MentorMatchesView,
    OpportunityTalentMatchesView,
    ProactiveSourcingView,
    SkillRoadmapMeView,
    TrustScoreForTalentView,
    TrustScoreMeView,
)


app_name = 'ai_engine'

urlpatterns = [
    # Legacy: standalone script wrapper
    path('match-cv/', MatchCVView.as_view(), name='match-cv'),

    # Trust Score
    path('trust-score/me/', TrustScoreMeView.as_view(), name='trust-score-me'),
    path('trust-score/talents/<int:talent_id>/', TrustScoreForTalentView.as_view(),
         name='trust-score-talent'),

    # Skill Roadmap
    path('skill-roadmap/me/', SkillRoadmapMeView.as_view(), name='skill-roadmap-me'),

    # Project <-> Talent Match (Org owner of opportunity)
    path('opportunities/<int:opportunity_id>/talent-matches/',
         OpportunityTalentMatchesView.as_view(), name='opportunity-talent-matches'),

    # Predictive Talent Sourcing (Org)
    path('organizations/<int:organization_id>/proactive-sourcing/',
         ProactiveSourcingView.as_view(), name='proactive-sourcing'),

    # Mentor <-> Mentee Match (Talent)
    path('mentor-matches/', MentorMatchesView.as_view(), name='mentor-matches'),

    # Mentee Progress Insight (Mentor pre-session brief)
    path('mentorships/<int:mentorship_id>/progress-insight/',
         MenteeProgressInsightView.as_view(), name='mentee-progress-insight'),

    # Curriculum Alignment (School)
    path('schools/<int:school_id>/curriculum-alignment/',
         CurriculumAlignmentView.as_view(), name='curriculum-alignment'),
]
