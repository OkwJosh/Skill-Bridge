"""
Talent Views for SkillBridge API
================================

Endpoints for managing talent profiles and skills.
All responses use the standard JSON envelope.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from .models import TalentProfile, TalentSkill
from .serializers import (
    TalentProfileSerializer,
    TalentProfileUpdateSerializer,
    TalentSkillSerializer,
    TalentSkillCreateSerializer,
)


class TalentProfileMeView(APIView):
    """
    GET /api/v1/talents/me/
    PATCH /api/v1/talents/me/
    
    Retrieve or update the authenticated user's talent profile.
    Creates the profile automatically if it doesn't exist.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/v1/talents/me/
        
        Returns the current user's talent profile with nested skills.
        Auto-creates profile if user is marked as talent but has no profile.
        """
        user = request.user
        
        # Ensure user has talent role
        if not user.is_talent:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "User is not registered as a talent. Set is_talent=True first.",
                    "code": "not_talent"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get or create talent profile
        profile, created = TalentProfile.objects.get_or_create(user=user)
        
        serializer = TalentProfileSerializer(profile)
        
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"created": created},
            "errors": []
        })
    
    def patch(self, request):
        """
        PATCH /api/v1/talents/me/
        
        Update the current user's talent profile.
        """
        user = request.user
        
        if not user.is_talent:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "User is not registered as a talent.",
                    "code": "not_talent"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Get or create profile
        profile, _ = TalentProfile.objects.get_or_create(user=user)
        
        serializer = TalentProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Return full profile after update
        return Response({
            "status": "success",
            "data": TalentProfileSerializer(profile).data,
            "meta": {},
            "errors": []
        })


class TalentListView(APIView):
    """
    GET /api/v1/talents/?search=&skills=&is_available=&ordering=

    Open-to-all-authenticated browse endpoint for the Talent Marketplace.
    Mentors and org admins both consume this from the /app/talent UI.

    Query params:
      search       — case-insensitive match on headline + user__full_name + institution_name
      skills       — comma-separated CanonicalSkill IDs (any-of match)
      is_available — 'true' / 'false'
      ordering     — '-updated_at' (default), 'headline', '-created_at'
      limit        — cap the response (default 50, max 100)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = (
            TalentProfile.objects
            .select_related('user')
            .prefetch_related('skills__skill')
        )

        # is_available
        is_available = request.query_params.get('is_available')
        if is_available is not None:
            qs = qs.filter(is_available=(is_available.lower() == 'true'))

        # skills (any-of match)
        skills_param = request.query_params.get('skills')
        if skills_param:
            ids = [int(x) for x in skills_param.split(',') if x.strip().isdigit()]
            if ids:
                qs = qs.filter(skills__skill_id__in=ids).distinct()

        # search
        search = request.query_params.get('search')
        if search:
            from django.db.models import Q
            qs = qs.filter(
                Q(headline__icontains=search) |
                Q(user__full_name__icontains=search) |
                Q(institution_name__icontains=search)
            )

        # ordering
        ordering = request.query_params.get('ordering', '-updated_at')
        if ordering in ('-updated_at', 'updated_at', 'headline', '-created_at', 'created_at'):
            qs = qs.order_by(ordering)

        # limit (capped)
        try:
            limit = int(request.query_params.get('limit', 50))
        except ValueError:
            limit = 50
        limit = max(1, min(limit, 100))

        from .serializers import TalentSearchSerializer
        data = TalentSearchSerializer(qs[:limit], many=True).data
        # Consistent list envelope: data array + meta.count (matches the
        # opportunities / applications / talent-search endpoints).
        return Response({
            "status": "success",
            "data": data,
            "meta": {"count": len(data)},
            "errors": [],
        })


class TalentDetailView(APIView):
    """
    GET /api/v1/talents/<id>/

    Any authenticated user can read any talent's public profile (used by
    mentors, org admins, and Trust Score viewers). Returns the same shape
    as `/talents/me/` minus the create-on-fetch behaviour.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, talent_id):
        profile = TalentProfile.objects.filter(pk=talent_id).first()
        if not profile:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 404},
                 'errors': [{'field': None, 'message': 'Talent not found.', 'code': 'not_found'}]},
                status=status.HTTP_404_NOT_FOUND,
            )
        return Response(TalentProfileSerializer(profile).data)


class TalentSkillManageView(APIView):
    """
    POST /api/v1/talents/me/skills/
    DELETE /api/v1/talents/me/skills/<skill_id>/
    
    Add or remove skills from the authenticated user's talent profile.
    """
    
    permission_classes = [IsAuthenticated]
    
    def _get_talent_profile(self, user):
        """Helper to get user's talent profile or return error response."""
        if not user.is_talent:
            return None, Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "User is not registered as a talent.",
                    "code": "not_talent"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        profile, _ = TalentProfile.objects.get_or_create(user=user)
        return profile, None
    
    def post(self, request):
        """
        POST /api/v1/talents/me/skills/
        
        Add a new skill to the talent's profile.
        
        Request Body:
        {
            "skill_id": 1,
            "proficiency": "intermediate",
            "years_experience": 2,
            "is_primary": false
        }
        """
        profile, error_response = self._get_talent_profile(request.user)
        if error_response:
            return error_response
        
        serializer = TalentSkillCreateSerializer(
            data=request.data,
            context={'talent': profile}
        )
        serializer.is_valid(raise_exception=True)
        
        # Create the TalentSkill
        talent_skill = TalentSkill.objects.create(
            talent=profile,
            skill_id=serializer.validated_data['skill_id'],
            proficiency=serializer.validated_data.get('proficiency', 'beginner'),
            years_experience=serializer.validated_data.get('years_experience', 0),
            is_primary=serializer.validated_data.get('is_primary', False),
        )
        
        return Response({
            "status": "success",
            "data": TalentSkillSerializer(talent_skill).data,
            "meta": {},
            "errors": []
        }, status=status.HTTP_201_CREATED)
    
    def delete(self, request, skill_id=None):
        """
        DELETE /api/v1/talents/me/skills/<skill_id>/
        
        Remove a skill from the talent's profile.
        skill_id is the CanonicalSkill ID, not TalentSkill ID.
        """
        profile, error_response = self._get_talent_profile(request.user)
        if error_response:
            return error_response
        
        if not skill_id:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 400},
                "errors": [{
                    "field": "skill_id",
                    "message": "skill_id is required in URL.",
                    "code": "required"
                }]
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find and delete the talent skill
        talent_skill = TalentSkill.objects.filter(
            talent=profile,
            skill_id=skill_id
        ).first()
        
        if not talent_skill:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "Skill not found in your profile.",
                    "code": "not_found"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        talent_skill.delete()
        
        return Response({
            "status": "success",
            "data": None,
            "meta": {"message": "Skill removed from profile."},
            "errors": []
        }, status=status.HTTP_200_OK)


class TalentSkillUpdateView(APIView):
    """
    PATCH /api/v1/talents/me/skills/<skill_id>/
    
    Update skill details (proficiency, years_experience, is_primary).
    """
    
    permission_classes = [IsAuthenticated]
    
    def patch(self, request, skill_id):
        """Update a talent's skill details."""
        user = request.user
        
        if not user.is_talent:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "User is not registered as a talent.",
                    "code": "not_talent"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            profile = user.talent_profile
        except TalentProfile.DoesNotExist:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "Talent profile not found.",
                    "code": "not_found"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        talent_skill = TalentSkill.objects.filter(
            talent=profile,
            skill_id=skill_id
        ).first()
        
        if not talent_skill:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 404},
                "errors": [{
                    "field": None,
                    "message": "Skill not found in your profile.",
                    "code": "not_found"
                }]
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Update allowed fields
        allowed_fields = ['proficiency', 'years_experience', 'is_primary']
        for field in allowed_fields:
            if field in request.data:
                setattr(talent_skill, field, request.data[field])
        
        talent_skill.save()
        
        return Response({
            "status": "success",
            "data": TalentSkillSerializer(talent_skill).data,
            "meta": {},
            "errors": []
        })

