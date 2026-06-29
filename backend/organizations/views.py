"""
Organization Views for SkillBridge API
======================================

Endpoints for managing organizations and proactive talent sourcing.
All responses use the standard JSON envelope.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Organization, OrganizationMember
from .serializers import (
    OrganizationSerializer,
    OrganizationUpdateSerializer,
)
from .filters import TalentSearchFilter
from talents.models import TalentProfile
from talents.serializers import TalentSearchSerializer


class OrganizationCreateView(APIView):
    """
    POST /api/v1/organizations/

    Lets a freshly-signed-up org admin create their first organization.
    The caller is automatically added as `OrganizationMember(role='owner')`,
    which is what `OrganizationMeView.GET` looks up.

    Returns 409 if the caller already belongs to an organization (we
    deliberately enforce one-org-per-user for now; multi-org membership
    is a future feature).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        if not request.user.is_org_admin:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 403},
                 'errors': [{'field': None,
                             'message': 'Only org admins can create an organization.',
                             'code': 'not_org_admin'}]},
                status=status.HTTP_403_FORBIDDEN,
            )

        existing = OrganizationMember.objects.filter(user=request.user).first()
        if existing:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 409},
                 'errors': [{'field': None,
                             'message': 'You already belong to an organization.',
                             'code': 'already_member'}]},
                status=status.HTTP_409_CONFLICT,
            )

        # Use the existing update serializer for input validation — same fields
        # are settable on create.
        serializer = OrganizationUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        name = serializer.validated_data.get('name', '').strip()
        if not name:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 400},
                 'errors': [{'field': 'name',
                             'message': 'Organization name is required.',
                             'code': 'required'}]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Generate a unique slug from the name.
        from django.utils.text import slugify
        base_slug = slugify(name)[:200] or 'org'
        slug = base_slug
        n = 2
        while Organization.objects.filter(slug=slug).exists():
            slug = f'{base_slug}-{n}'
            n += 1

        industry_id = serializer.validated_data.pop('industry_id', None)
        org = Organization.objects.create(slug=slug, **serializer.validated_data)
        if industry_id:
            from core.models import CanonicalIndustry
            ind = CanonicalIndustry.objects.filter(pk=industry_id, is_active=True).first()
            if ind:
                org.industry = ind
                org.save(update_fields=['industry'])

        OrganizationMember.objects.create(
            organization=org, user=request.user,
            role=OrganizationMember.MemberRole.OWNER,
        )

        return Response(OrganizationSerializer(org).data, status=status.HTTP_201_CREATED)


class OrganizationMeView(APIView):
    """
    GET /api/v1/organizations/me/
    PATCH /api/v1/organizations/me/
    
    Retrieve or update the organization the logged-in user belongs to.
    User must be an org_admin and have an organization membership.
    """
    
    permission_classes = [IsAuthenticated]
    
    def _get_user_organization(self, user):
        """
        Helper to get the organization the user belongs to.
        Returns (organization, membership, error_response).
        """
        if not user.is_org_admin:
            return None, None, Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "User is not an organization admin. Set is_org_admin=True first.",
                    "code": "not_org_admin"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Find user's organization membership
        membership = OrganizationMember.objects.filter(user=user).select_related('organization').first()
        
        if not membership:
            return None, None, Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "User is not a member of any organization.",
                    "code": "no_organization"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        return membership.organization, membership, None
    
    def get(self, request):
        """
        GET /api/v1/organizations/me/
        
        Returns the organization the current user belongs to.
        """
        organization, membership, error_response = self._get_user_organization(request.user)
        if error_response:
            return error_response
        
        serializer = OrganizationSerializer(organization)
        
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {
                "user_role": membership.role,
            },
            "errors": []
        })
    
    def patch(self, request):
        """
        PATCH /api/v1/organizations/me/
        
        Update the organization.
        Only owners and admins can update.
        """
        organization, membership, error_response = self._get_user_organization(request.user)
        if error_response:
            return error_response
        
        # Check permission (only owner/admin can update)
        if membership.role not in ['owner', 'admin']:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "Only organization owners and admins can update organization details.",
                    "code": "insufficient_permission"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        serializer = OrganizationUpdateSerializer(
            organization,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            "status": "success",
            "data": OrganizationSerializer(organization).data,
            "meta": {},
            "errors": []
        })


class TalentSearchView(ListAPIView):
    """
    GET /api/v1/organizations/me/talent-search/
    
    Proactive talent sourcing endpoint.
    Allows organizations to search and filter talent profiles.
    
    Query Parameters:
    - skills: Comma-separated CanonicalSkill IDs (e.g., ?skills=1,2,3)
    - education_route: Filter by education (university, polytechnic, bootcamp, self_taught)
    - is_school_verified: Filter by verification status (true/false)
    - is_available: Filter by availability (true/false)
    - city: Filter by city (partial match)
    - state: Filter by state (partial match)
    - search: Full-text search on headline, bio
    - ordering: Sort by field (e.g., -created_at, headline)
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = TalentSearchSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = TalentSearchFilter
    search_fields = ['headline', 'bio', 'user__full_name', 'institution_name']
    ordering_fields = ['created_at', 'updated_at', 'headline']
    ordering = ['-updated_at']
    
    def get_queryset(self):
        """
        Return only available talent profiles.
        Prefetch skills for performance.
        """
        return TalentProfile.objects.filter(
            is_available=True
        ).select_related(
            'user'
        ).prefetch_related(
            'skills',
            'skills__skill'
        ).distinct()
    
    def list(self, request, *args, **kwargs):
        """Override list to use standard envelope."""
        # Verify user is org admin
        if not request.user.is_org_admin:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "Only organization admins can search talents.",
                    "code": "not_org_admin"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        queryset = self.filter_queryset(self.get_queryset())
        
        # Paginate
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Get pagination data
            return Response({
                "status": "success",
                "data": serializer.data,
                "meta": {
                    "count": self.paginator.page.paginator.count,
                    "page_size": self.paginator.page_size,
                    "current_page": self.paginator.page.number,
                    "total_pages": self.paginator.page.paginator.num_pages,
                },
                "errors": []
            })
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"count": len(serializer.data)},
            "errors": []
        })

