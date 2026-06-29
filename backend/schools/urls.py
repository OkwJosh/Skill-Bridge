"""
School URL Routes for SkillBridge API
=====================================

All routes prefixed with /api/v1/schools/ (configured in config/urls.py)
"""

from django.urls import path
from .views import (
    SchoolCreateView,
    SchoolMeView,
    SchoolRosterView,
    SchoolRosterCSVImportView,
    ConsentToSchoolDataView,
    VerificationStatusView,
)

app_name = 'schools'

urlpatterns = [
    # POST /api/v1/schools/ - first-time setup for a school admin
    path('', SchoolCreateView.as_view(), name='school-create'),

    # School Admin Endpoints
    # GET /api/v1/schools/me/ - Get current user's school
    path('me/', SchoolMeView.as_view(), name='school-me'),

    # GET  /api/v1/schools/me/roster/ - List student roster
    # POST /api/v1/schools/me/roster/ - Add student to roster
    path('me/roster/', SchoolRosterView.as_view(), name='roster'),

    # POST /api/v1/schools/me/roster/import/ - bulk-import roster from CSV
    path('me/roster/import/', SchoolRosterCSVImportView.as_view(), name='roster-import'),

    # Talent Endpoints
    # POST /api/v1/schools/consent/ - Consent to school data sharing
    path('consent/', ConsentToSchoolDataView.as_view(), name='consent'),

    # GET /api/v1/schools/verification-status/ - Check verification status
    path('verification-status/', VerificationStatusView.as_view(), name='verification-status'),
]
