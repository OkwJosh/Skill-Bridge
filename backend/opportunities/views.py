"""
Opportunity Views for SkillBridge API
=====================================

Endpoints for opportunities and applications.
All responses use the standard JSON envelope.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.utils import timezone
from django.db.models import Q, Count

from .models import Opportunity, Application, OpportunityStatus, ApplicationStatus, SavedOpportunity, ApplicationInterview
from .serializers import (
    OpportunitySerializer,
    OpportunityListSerializer,
    OpportunityCreateSerializer,
    OpportunityUpdateSerializer,
    ApplicationSerializer,
    ApplicationCreateSerializer,
    ApplicationCreateSerializer,
    ApplicationStatusUpdateSerializer,
    ApplicationInterviewSerializer,
)
from .filters import OpportunityFilter
from talents.models import TalentProfile
from organizations.models import OrganizationMember
from mentors.models import MentorProfile


class OpportunityListCreateView(APIView):
    """
    GET /api/v1/opportunities/
    POST /api/v1/opportunities/
    
    GET: Public listing of open opportunities (no auth required).
    POST: Create a new opportunity (requires auth, must be org admin or mentor).
    """
    
    def get_permissions(self):
        """GET is public, POST requires auth."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get(self, request):
        """
        GET /api/v1/opportunities/
        
        Public listing of opportunities.
        Supports search and filtering.
        
        Query params:
        - search: Full-text search on title, description
        - opportunity_type: Filter by type
        - is_remote: Filter remote opportunities
        - is_paid: Filter paid opportunities
        - skills: Filter by required skill IDs (comma-separated)
        - category_id: Filter by category ID
        - organization: Filter by organization ID
        """
        queryset = Opportunity.objects.select_related(
            'organization', 'mentor__user'
        ).prefetch_related(
            'required_skills'
        ).annotate(
            application_count=Count('applications', distinct=True)
        )

        # Parse the organization filter defensively so bad input (?organization=abc)
        # returns an empty list rather than a 500.
        org_raw = request.query_params.get('organization')
        organization = int(org_raw) if (org_raw and org_raw.isdigit()) else None

        # Status visibility: public callers only ever see OPEN opportunities.
        # An authenticated member of the requested org sees ALL of that org's
        # postings (draft/closed/filled) so their dashboard is complete. A
        # `status` query param narrows it further.
        viewing_own_org = bool(
            organization
            and request.user.is_authenticated
            and OrganizationMember.objects.filter(
                user=request.user, organization_id=organization
            ).exists()
        )
        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)
        elif not viewing_own_org:
            queryset = queryset.filter(status=OpportunityStatus.OPEN)

        # Search
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search)
            )

        # Filtering
        opportunity_type = request.query_params.get('opportunity_type')
        if opportunity_type:
            queryset = queryset.filter(opportunity_type=opportunity_type)

        is_remote = request.query_params.get('is_remote')
        if is_remote is not None:
            queryset = queryset.filter(is_remote=is_remote.lower() == 'true')

        is_paid = request.query_params.get('is_paid')
        if is_paid is not None:
            queryset = queryset.filter(is_paid=is_paid.lower() == 'true')

        skills = request.query_params.get('skills')
        if skills:
            skill_ids = [int(s) for s in skills.split(',') if s.isdigit()]
            queryset = queryset.filter(required_skills__id__in=skill_ids).distinct()

        category_id = request.query_params.get('category_id')
        if category_id and category_id.isdigit():
            queryset = queryset.filter(category_id=int(category_id))

        if organization:
            queryset = queryset.filter(organization_id=organization)

        # Ordering
        ordering = request.query_params.get('ordering', '-created_at')
        if ordering in ['created_at', '-created_at', 'title', '-title', 'application_deadline']:
            queryset = queryset.order_by(ordering)
        else:
            queryset = queryset.order_by('-created_at')

        serializer = OpportunityListSerializer(queryset, many=True)

        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"count": len(serializer.data)},
            "errors": []
        })
    
    def post(self, request):
        """
        POST /api/v1/opportunities/
        
        Create a new opportunity.
        User must be an org admin or mentor.
        """
        user = request.user
        
        # Determine poster type
        organization = None
        mentor = None
        
        if user.is_org_admin:
            # Get user's organization
            membership = OrganizationMember.objects.filter(user=user).first()
            if membership:
                organization = membership.organization
        
        if user.is_mentor and not organization:
            # Check if mentor profile exists
            try:
                mentor = user.mentor_profile
            except MentorProfile.DoesNotExist:
                mentor = MentorProfile.objects.create(user=user)
        
        if not organization and not mentor:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "You must be an organization admin or mentor to post opportunities.",
                    "code": "not_authorized"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OpportunityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        opportunity = serializer.save(
            organization=organization,
            mentor=mentor,
            created_by=user
        )
        
        return Response({
            "status": "success",
            "data": OpportunitySerializer(opportunity).data,
            "meta": {"message": "Opportunity created successfully."},
            "errors": []
        }, status=status.HTTP_201_CREATED)


class OpportunityDetailView(APIView):
    """
    GET /api/v1/opportunities/<pk>/
    PATCH /api/v1/opportunities/<pk>/
    
    GET: Public - retrieve opportunity details.
    PATCH: Requires auth - update opportunity (only owner).
    """
    
    def get_permissions(self):
        """GET is public, PATCH requires auth."""
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAuthenticated()]
    
    def get_opportunity(self, pk):
        """Helper to get opportunity or None."""
        try:
            return Opportunity.objects.select_related(
                'organization', 'mentor__user'
            ).prefetch_related(
                'required_skills'
            ).get(pk=pk)
        except Opportunity.DoesNotExist:
            return None
    
    def get(self, request, pk):
        """GET /api/v1/opportunities/<pk>/"""
        opportunity = self.get_opportunity(pk)
        
        if not opportunity:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "Opportunity not found.",
                    "code": "not_found"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        serializer = OpportunitySerializer(opportunity)
        
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {},
            "errors": []
        })
    
    def patch(self, request, pk):
        """PATCH /api/v1/opportunities/<pk>/"""
        opportunity = self.get_opportunity(pk)
        
        if not opportunity:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "Opportunity not found.",
                    "code": "not_found"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check ownership
        user = request.user
        is_owner = False
        
        if opportunity.organization:
            membership = OrganizationMember.objects.filter(
                user=user,
                organization=opportunity.organization,
                role__in=['owner', 'admin']
            ).exists()
            is_owner = membership
        elif opportunity.mentor and opportunity.mentor.user == user:
            is_owner = True
        
        if not is_owner:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "You don't have permission to update this opportunity.",
                    "code": "not_owner"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OpportunityUpdateSerializer(
            opportunity,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "status": "success",
            "data": OpportunitySerializer(opportunity).data,
            "meta": {},
            "errors": []
        })


class ApplicationCreateView(APIView):
    """
    POST /api/v1/opportunities/<opportunity_id>/apply/
    
    Allows a talent to apply to an opportunity.
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, opportunity_id):
        """Create an application for an opportunity."""
        user = request.user
        
        # Verify user is a talent
        if not user.is_talent:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "Only talents can apply to opportunities.",
                    "code": "not_talent"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get talent profile
        try:
            talent_profile = user.talent_profile
        except TalentProfile.DoesNotExist:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 400},
                "errors": [{
                    "field": None,
                    "message": "Please complete your talent profile before applying.",
                    "code": "no_profile"
                }]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get opportunity
        try:
            opportunity = Opportunity.objects.get(pk=opportunity_id)
        except Opportunity.DoesNotExist:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "Opportunity not found.",
                    "code": "not_found"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Check if opportunity is open
        if opportunity.status != OpportunityStatus.OPEN:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 400},
                "errors": [{
                    "field": None,
                    "message": "This opportunity is not accepting applications.",
                    "code": "not_open"
                }]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check for duplicate application
        if Application.objects.filter(opportunity=opportunity, talent=talent_profile).exists():
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 409},
                "errors": [{
                    "field": None,
                    "message": "You have already applied to this opportunity.",
                    "code": "duplicate"
                }]
            }, status=status.HTTP_409_CONFLICT)
        
        serializer = ApplicationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        application = Application.objects.create(
            opportunity=opportunity,
            talent=talent_profile,
            **serializer.validated_data
        )
        
        return Response({
            "status": "success",
            "data": ApplicationSerializer(application).data,
            "meta": {"message": "Application submitted successfully."},
            "errors": []
        }, status=status.HTTP_201_CREATED)


class ApplicationStatusUpdateView(APIView):
    """
    PATCH /api/v1/opportunities/applications/<pk>/status/
    
    Allows the opportunity owner to update application status.
    """
    
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, pk):
        """Update application status."""
        user = request.user
        
        # Get application
        try:
            application = Application.objects.select_related(
                'opportunity__organization',
                'opportunity__mentor__user',
                'talent__user'
            ).get(pk=pk)
        except Application.DoesNotExist:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "Application not found.",
                    "code": "not_found"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        opportunity = application.opportunity
        
        # Verify ownership
        is_owner = False
        
        if opportunity.organization:
            membership = OrganizationMember.objects.filter(
                user=user,
                organization=opportunity.organization,
                role__in=['owner', 'admin']
            ).exists()
            is_owner = membership
        elif opportunity.mentor and opportunity.mentor.user == user:
            is_owner = True
        
        if not is_owner:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "You don't have permission to update this application.",
                    "code": "not_owner"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = ApplicationStatusUpdateSerializer(
            application,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        # Update application
        application.status = serializer.validated_data['status']
        application.reviewer_notes = serializer.validated_data.get('reviewer_notes', application.reviewer_notes)
        application.reviewed_by = user
        application.reviewed_at = timezone.now()
        application.save()
        
        return Response({
            "status": "success",
            "data": ApplicationSerializer(application).data,
            "meta": {"message": f"Application status updated to '{application.status}'."},
            "errors": []
        })


class MyApplicationsView(APIView):
    """
    GET /api/v1/opportunities/my-applications/
    
    List all applications for the current talent.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List current user's applications."""
        user = request.user
        
        if not user.is_talent:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "Only talents can view applications.",
                    "code": "not_talent"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            talent_profile = user.talent_profile
        except TalentProfile.DoesNotExist:
            return Response({
                "status": "success",
                "data": [],
                "meta": {"count": 0},
                "errors": []
            })
        
        applications = Application.objects.filter(
            talent=talent_profile
        ).select_related(
            'opportunity', 'opportunity__organization', 'opportunity__mentor__user',
        ).order_by('-created_at')
        
        serializer = ApplicationSerializer(applications, many=True)
        
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"count": len(serializer.data)},
            "errors": []
        })


class OpportunityApplicationsView(APIView):
    """
    GET /api/v1/opportunities/<pk>/applications/
    
    List all applications for an opportunity (owner only).
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request, pk):
        """List applications for an opportunity."""
        user = request.user
        
        try:
            opportunity = Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "Opportunity not found.",
                    "code": "not_found"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Verify ownership
        is_owner = False
        
        if opportunity.organization:
            membership = OrganizationMember.objects.filter(
                user=user,
                organization=opportunity.organization,
                role__in=['owner', 'admin', 'member']
            ).exists()
            is_owner = membership
        elif opportunity.mentor and opportunity.mentor.user == user:
            is_owner = True
        
        if not is_owner:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "You don't have permission to view these applications.",
                    "code": "not_owner"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Filter by status if provided
        status_filter = request.query_params.get('status')
        applications = opportunity.applications.select_related('talent__user')
        
        if status_filter:
            applications = applications.filter(status=status_filter)
        
        applications = applications.order_by('-created_at')
        serializer = ApplicationSerializer(applications, many=True)
        
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"count": len(serializer.data)},
            "errors": []
        })


class SavedOpportunityToggleView(APIView):
    """
    POST /api/v1/opportunities/<pk>/save/
    DELETE /api/v1/opportunities/<pk>/save/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            opportunity = Opportunity.objects.get(pk=pk)
        except Opportunity.DoesNotExist:
            return Response({"status": "error", "errors": [{"message": "Opportunity not found."}]}, status=status.HTTP_404_NOT_FOUND)
        
        SavedOpportunity.objects.get_or_create(user=request.user, opportunity=opportunity)
        return Response({"status": "success", "meta": {"message": "Opportunity saved successfully."}}, status=status.HTTP_201_CREATED)

    def delete(self, request, pk):
        SavedOpportunity.objects.filter(user=request.user, opportunity_id=pk).delete()
        return Response({"status": "success", "meta": {"message": "Opportunity unsaved successfully."}}, status=status.HTTP_200_OK)


class SavedOpportunityListView(APIView):
    """
    GET /api/v1/opportunities/saved/
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        saved = SavedOpportunity.objects.filter(user=request.user).select_related('opportunity')
        opportunities = [s.opportunity for s in saved]
        serializer = OpportunityListSerializer(opportunities, many=True, context={'request': request})
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"count": len(serializer.data)},
            "errors": []
        })


class ApplicationInterviewCreateView(APIView):
    """
    POST /api/v1/opportunities/applications/<pk>/interviews/
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            application = Application.objects.select_related('opportunity__organization', 'opportunity__mentor__user').get(pk=pk)
        except Application.DoesNotExist:
            return Response({"status": "error", "errors": [{"message": "Application not found."}]}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        opportunity = application.opportunity
        is_owner = False
        
        if opportunity.organization:
            membership = OrganizationMember.objects.filter(
                user=user,
                organization=opportunity.organization,
                role__in=['owner', 'admin']
            ).exists()
            is_owner = membership
        elif opportunity.mentor and opportunity.mentor.user == user:
            is_owner = True
        
        if not is_owner:
            return Response({"status": "error", "errors": [{"message": "You don't have permission."}]}, status=status.HTTP_403_FORBIDDEN)

        serializer = ApplicationInterviewSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(application=application)

        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"message": "Interview scheduled successfully."},
            "errors": []
        }, status=status.HTTP_201_CREATED)
