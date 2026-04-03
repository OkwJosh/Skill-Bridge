"""
Mentor Views for SkillBridge API
================================

Endpoints for mentor profiles and skill endorsements.
All responses use the standard JSON envelope.
"""

from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone

from .models import MentorProfile
from .serializers import (
    MentorProfileSerializer,
    MentorProfileUpdateSerializer,
    EndorsementCreateSerializer,
    EndorsementResponseSerializer,
)
from talents.models import TalentSkill


class MentorMeView(APIView):
    """
    GET /api/v1/mentors/me/
    PATCH /api/v1/mentors/me/
    
    Retrieve or update the authenticated user's mentor profile.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        GET /api/v1/mentors/me/
        
        Returns the current user's mentor profile.
        Auto-creates profile if user is marked as mentor but has no profile.
        """
        user = request.user
        
        if not user.is_mentor:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "User is not registered as a mentor. Set is_mentor=True first.",
                    "code": "not_mentor"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        profile, created = MentorProfile.objects.get_or_create(user=user)
        serializer = MentorProfileSerializer(profile)
        
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"created": created},
            "errors": []
        })
    
    def patch(self, request):
        """
        PATCH /api/v1/mentors/me/
        
        Update the current user's mentor profile.
        """
        user = request.user
        
        if not user.is_mentor:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "User is not registered as a mentor.",
                    "code": "not_mentor"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        profile, _ = MentorProfile.objects.get_or_create(user=user)
        
        serializer = MentorProfileUpdateSerializer(
            profile,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        
        # Handle expertise_area_ids manually
        expertise_ids = serializer.validated_data.pop('expertise_area_ids', None)
        
        for attr, value in serializer.validated_data.items():
            setattr(profile, attr, value)
        profile.save()
        
        if expertise_ids is not None:
            from core.models import CanonicalSkill
            skills = CanonicalSkill.objects.filter(id__in=expertise_ids, is_active=True)
            profile.expertise_areas.set(skills)
        
        return Response({
            "status": "success",
            "data": MentorProfileSerializer(profile).data,
            "meta": {},
            "errors": []
        })


class MentorEndorsementCreateView(APIView):
    """
    POST /api/v1/mentors/me/endorsements/
    
    Allows a mentor to endorse a talent's skill.
    
    Request Body:
    {
        "talent_profile_id": 1,
        "skill_id": 5,
        "endorsement_note": "Excellent Python skills demonstrated in project X"
    }
    """
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """Create a skill endorsement."""
        user = request.user
        
        # Verify user is a mentor
        if not user.is_mentor:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "Only mentors can endorse skills.",
                    "code": "not_mentor"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Ensure mentor profile exists
        try:
            mentor_profile = user.mentor_profile
        except MentorProfile.DoesNotExist:
            mentor_profile = MentorProfile.objects.create(user=user)
        
        serializer = EndorsementCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        talent_skill = serializer.validated_data['talent_skill']
        endorsement_note = serializer.validated_data.get('endorsement_note', '')
        
        # Update the TalentSkill with endorsement
        talent_skill.is_endorsed = True
        talent_skill.endorsed_by = user
        talent_skill.endorsed_at = timezone.now()
        talent_skill.endorsement_note = endorsement_note
        talent_skill.save()
        
        # Update mentor's endorsement count
        mentor_profile.endorsements_given += 1
        mentor_profile.save(update_fields=['endorsements_given'])
        
        return Response({
            "status": "success",
            "data": EndorsementResponseSerializer(talent_skill).data,
            "meta": {"message": "Skill endorsed successfully."},
            "errors": []
        }, status=status.HTTP_201_CREATED)


class MentorEndorsementListView(APIView):
    """
    GET /api/v1/mentors/me/endorsements/
    
    List all endorsements given by the current mentor.
    """
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """List endorsements given by this mentor."""
        user = request.user
        
        if not user.is_mentor:
            return Response({
                "status": "error",
                "data": None,
                "meta": {"http_status": 403},
                "errors": [{
                    "field": None,
                    "message": "Only mentors can view endorsements.",
                    "code": "not_mentor"
                }]
            }, status=status.HTTP_403_FORBIDDEN)
        
        endorsements = TalentSkill.objects.filter(
            endorsed_by=user,
            is_endorsed=True
        ).select_related('talent__user', 'skill')
        
        serializer = EndorsementResponseSerializer(endorsements, many=True)
        
        return Response({
            "status": "success",
            "data": serializer.data,
            "meta": {"count": len(serializer.data)},
            "errors": []
        })

