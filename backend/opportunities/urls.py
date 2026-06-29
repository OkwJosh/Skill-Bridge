"""
Opportunity URL Routes for SkillBridge API
==========================================

All routes prefixed with /api/v1/opportunities/ (configured in config/urls.py)
"""

from django.urls import path
from .views import (
    OpportunityListCreateView,
    OpportunityDetailView,
    ApplicationCreateView,
    ApplicationStatusUpdateView,
    MyApplicationsView,
    OpportunityApplicationsView,
    SavedOpportunityToggleView,
    SavedOpportunityListView,
    ApplicationInterviewCreateView,
)

app_name = 'opportunities'

urlpatterns = [
    # Opportunities
    # GET  /api/v1/opportunities/ - List opportunities (public)
    # POST /api/v1/opportunities/ - Create opportunity (auth required)
    path('', OpportunityListCreateView.as_view(), name='list-create'),
    
    # GET /api/v1/opportunities/saved/ - List saved opportunities
    path('saved/', SavedOpportunityListView.as_view(), name='saved-list'),

    # GET  /api/v1/opportunities/<pk>/ - Get opportunity details (public)
    # PATCH /api/v1/opportunities/<pk>/ - Update opportunity (owner only)
    path('<int:pk>/', OpportunityDetailView.as_view(), name='detail'),

    # POST /api/v1/opportunities/<pk>/save/ - Save opportunity
    # DELETE /api/v1/opportunities/<pk>/save/ - Unsave opportunity
    path('<int:pk>/save/', SavedOpportunityToggleView.as_view(), name='save-toggle'),
    
    # Applications
    # POST /api/v1/opportunities/<opportunity_id>/apply/ - Apply to opportunity
    path('<int:opportunity_id>/apply/', ApplicationCreateView.as_view(), name='apply'),
    
    # GET /api/v1/opportunities/<pk>/applications/ - List applications for opportunity (owner)
    path('<int:pk>/applications/', OpportunityApplicationsView.as_view(), name='applications'),
    
    # PATCH /api/v1/opportunities/applications/<pk>/status/ - Update application status
    path('applications/<int:pk>/status/', ApplicationStatusUpdateView.as_view(), name='application-status'),
    
    # POST /api/v1/opportunities/applications/<pk>/interviews/ - Schedule interview
    path('applications/<int:pk>/interviews/', ApplicationInterviewCreateView.as_view(), name='application-interviews'),
    
    # GET /api/v1/opportunities/my-applications/ - List my applications (talent)
    path('my-applications/', MyApplicationsView.as_view(), name='my-applications'),
]
