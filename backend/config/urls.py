"""
SkillBridge URL Configuration
=============================

API Routes:
    /admin/                     - Django Admin
    /api/v1/auth/               - Authentication & user profile
    /api/v1/talents/            - Talent profiles & skills
    /api/v1/organizations/      - Organization management & talent search
    /api/v1/mentors/            - Mentor profiles & endorsements
    /api/v1/opportunities/      - Opportunities & applications
    /api/v1/schools/            - School admin & verification
    /api/v1/health/             - Health check
    /api/schema/                - OpenAPI schema (JSON)
    /api/docs/                  - Swagger UI documentation
"""

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from users.views import HealthCheckView

def health(request):
    return HttpResponse("OK")

urlpatterns = [
    # Simple root-level health check (no DB, no auth)
    path('health', health, name='simple-health-check'),
    
    # Django Admin
    path('admin/', admin.site.urls),
    
    # ==========================================================================
    # API v1 Routes
    # ==========================================================================
    
    # Authentication & User Profile
    path('api/v1/auth/', include('users.urls', namespace='users')),

    # Core taxonomy (skills, industries) — public read
    path('api/v1/core/', include('core.urls', namespace='core')),
    
    # Talent Profiles & Skills
    path('api/v1/talents/', include('talents.urls', namespace='talents')),
    
    # Organizations & Talent Search
    path('api/v1/organizations/', include('organizations.urls', namespace='organizations')),
    
    # Mentor Profiles & Endorsements
    path('api/v1/mentors/', include('mentors.urls', namespace='mentors')),
    
    # Opportunities & Applications
    path('api/v1/opportunities/', include('opportunities.urls', namespace='opportunities')),
    
    # Schools & Verification (Data Trust)
    path('api/v1/schools/', include('schools.urls', namespace='schools')),

    # AI Engine (CV matching, trust scoring)
    path('api/v1/ai/', include('ai_engine.urls', namespace='ai_engine')),

    # Notifications (in-app feed)
    path('api/v1/notifications/', include('notifications.urls', namespace='notifications')),

    # Health Check (no auth required)
    path('api/v1/health/', HealthCheckView.as_view(), name='health-check'),
    
    # ==========================================================================
    # API Documentation
    # ==========================================================================
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

