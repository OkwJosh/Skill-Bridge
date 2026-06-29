"""
Mentorship CRUD views.

Two surfaces of the same data:
  /api/v1/mentors/me/...    — mentor-side (full read/write incl. private_notes)
  /api/v1/talents/me/...    — talent-side (relationships read-only, sessions
                              read-only without private_notes, activities CRUD)

All responses follow the standard envelope wrapped by core.renderers.
"""

from django.db import IntegrityError
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from core.exceptions import Conflict
from talents.models import TalentProfile

from .models import MentorProfile, MentorSession, MentorshipRelationship, MenteeActivity
from .mentorship_serializers import (
    MenteeActivityCreateSerializer,
    MenteeActivitySerializer,
    MenteeActivityUpdateSerializer,
    MentorSessionCreateSerializer,
    MentorSessionMentorViewSerializer,
    MentorSessionTalentViewSerializer,
    MentorshipCreateSerializer,
    MentorshipRelationshipSerializer,
    MentorshipUpdateSerializer,
)


# =============================================================================
# Shared helpers
# =============================================================================

def _require_mentor_profile(user) -> MentorProfile:
    """Resolve the calling user's mentor profile or 403."""
    if not getattr(user, 'is_mentor', False):
        raise PermissionDenied('Only mentors can access this resource.')
    profile, _ = MentorProfile.objects.get_or_create(user=user)
    return profile


def _require_talent_profile(user) -> TalentProfile:
    """Resolve the calling user's talent profile or 403/404."""
    profile = getattr(user, 'talent_profile', None)
    if profile is None:
        raise PermissionDenied('You do not have a talent profile.')
    return profile


def _get_mentor_relationship(mentor_profile: MentorProfile, mentorship_id: int) -> MentorshipRelationship:
    try:
        rel = MentorshipRelationship.objects.select_related(
            'mentor__user', 'talent__user'
        ).get(pk=mentorship_id)
    except MentorshipRelationship.DoesNotExist:
        raise NotFound('Mentorship not found.')
    if rel.mentor_id != mentor_profile.id:
        raise PermissionDenied('You are not the mentor in this relationship.')
    return rel


def _get_talent_relationship(talent_profile: TalentProfile, mentorship_id: int) -> MentorshipRelationship:
    try:
        rel = MentorshipRelationship.objects.select_related(
            'mentor__user', 'talent__user'
        ).get(pk=mentorship_id)
    except MentorshipRelationship.DoesNotExist:
        raise NotFound('Mentorship not found.')
    if rel.talent_id != talent_profile.id:
        raise PermissionDenied('You are not the talent in this relationship.')
    return rel


# =============================================================================
# MENTOR SIDE: Mentorship Relationships
# =============================================================================

class MentorMentorshipListCreateView(APIView):
    """
    GET  /api/v1/mentors/me/mentorships/         — list mentor's mentorships
    POST /api/v1/mentors/me/mentorships/         — create relationship
    """

    def get(self, request):
        mentor = _require_mentor_profile(request.user)
        qs = MentorshipRelationship.objects.filter(mentor=mentor).select_related(
            'mentor__user', 'talent__user'
        )
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        data = MentorshipRelationshipSerializer(qs, many=True).data
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        mentor = _require_mentor_profile(request.user)
        serializer = MentorshipCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            rel = MentorshipRelationship.objects.create(
                mentor=mentor,
                talent_id=serializer.validated_data['talent_profile_id'],
                focus_area=serializer.validated_data.get('focus_area', ''),
            )
        except IntegrityError:
            raise Conflict('A mentorship with this talent already exists.')
        return Response(
            MentorshipRelationshipSerializer(rel).data,
            status=status.HTTP_201_CREATED,
        )


class MentorMentorshipDetailView(APIView):
    """
    GET   /api/v1/mentors/me/mentorships/<id>/   — detail
    PATCH /api/v1/mentors/me/mentorships/<id>/   — update status/focus_area
    """

    def get(self, request, mentorship_id):
        mentor = _require_mentor_profile(request.user)
        rel = _get_mentor_relationship(mentor, mentorship_id)
        return Response(MentorshipRelationshipSerializer(rel).data, status=status.HTTP_200_OK)

    def patch(self, request, mentorship_id):
        mentor = _require_mentor_profile(request.user)
        rel = _get_mentor_relationship(mentor, mentorship_id)
        serializer = MentorshipUpdateSerializer(rel, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        prior_status = rel.status
        instance = serializer.save()
        # Stamp ended_at when transitioning into ENDED.
        if (instance.status == MentorshipRelationship.Status.ENDED
                and prior_status != MentorshipRelationship.Status.ENDED):
            instance.ended_at = timezone.now()
            instance.save(update_fields=['ended_at'])
        return Response(MentorshipRelationshipSerializer(instance).data, status=status.HTTP_200_OK)


# =============================================================================
# MENTOR SIDE: Sessions
# =============================================================================

class MentorSessionListCreateView(APIView):
    """
    GET  /api/v1/mentors/me/mentorships/<id>/sessions/  — list sessions
    POST /api/v1/mentors/me/mentorships/<id>/sessions/  — create session
    """

    def get(self, request, mentorship_id):
        mentor = _require_mentor_profile(request.user)
        rel = _get_mentor_relationship(mentor, mentorship_id)
        sessions = MentorSession.objects.filter(relationship=rel)
        return Response(
            MentorSessionMentorViewSerializer(sessions, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, mentorship_id):
        mentor = _require_mentor_profile(request.user)
        rel = _get_mentor_relationship(mentor, mentorship_id)
        serializer = MentorSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        session = MentorSession.objects.create(relationship=rel, **serializer.validated_data)
        return Response(
            MentorSessionMentorViewSerializer(session).data,
            status=status.HTTP_201_CREATED,
        )


class MentorSessionDetailView(APIView):
    """
    GET    /api/v1/mentors/me/sessions/<id>/   — session detail
    PATCH  /api/v1/mentors/me/sessions/<id>/   — update (notes, status, time)
    DELETE /api/v1/mentors/me/sessions/<id>/   — delete
    """

    def _get_session(self, user, session_id):
        mentor = _require_mentor_profile(user)
        try:
            session = MentorSession.objects.select_related('relationship').get(pk=session_id)
        except MentorSession.DoesNotExist:
            raise NotFound('Session not found.')
        if session.relationship.mentor_id != mentor.id:
            raise PermissionDenied('You do not own this session.')
        return session

    def get(self, request, session_id):
        session = self._get_session(request.user, session_id)
        return Response(MentorSessionMentorViewSerializer(session).data, status=status.HTTP_200_OK)

    def patch(self, request, session_id):
        session = self._get_session(request.user, session_id)
        serializer = MentorSessionMentorViewSerializer(session, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, session_id):
        session = self._get_session(request.user, session_id)
        session.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# =============================================================================
# MENTOR SIDE: Read mentee activities
# =============================================================================

class MentorActivityListView(APIView):
    """GET /api/v1/mentors/me/mentorships/<id>/activities/   — read activities."""

    def get(self, request, mentorship_id):
        mentor = _require_mentor_profile(request.user)
        rel = _get_mentor_relationship(mentor, mentorship_id)
        activities = MenteeActivity.objects.filter(relationship=rel)
        return Response(
            MenteeActivitySerializer(activities, many=True).data,
            status=status.HTTP_200_OK,
        )


# =============================================================================
# TALENT SIDE: Read relationships
# =============================================================================

class TalentMentorshipListView(APIView):
    """GET /api/v1/talents/me/mentorships/   — talent lists their mentors."""

    def get(self, request):
        talent = _require_talent_profile(request.user)
        qs = MentorshipRelationship.objects.filter(talent=talent).select_related(
            'mentor__user', 'talent__user'
        )
        status_filter = request.query_params.get('status')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return Response(
            MentorshipRelationshipSerializer(qs, many=True).data,
            status=status.HTTP_200_OK,
        )


class TalentMentorshipDetailView(APIView):
    """GET /api/v1/talents/me/mentorships/<id>/   — single relationship."""

    def get(self, request, mentorship_id):
        talent = _require_talent_profile(request.user)
        rel = _get_talent_relationship(talent, mentorship_id)
        return Response(MentorshipRelationshipSerializer(rel).data, status=status.HTTP_200_OK)


# =============================================================================
# TALENT SIDE: Read sessions (without private_notes)
# =============================================================================

class TalentSessionListView(APIView):
    """GET /api/v1/talents/me/mentorships/<id>/sessions/   — sessions w/o notes."""

    def get(self, request, mentorship_id):
        talent = _require_talent_profile(request.user)
        rel = _get_talent_relationship(talent, mentorship_id)
        sessions = MentorSession.objects.filter(relationship=rel)
        return Response(
            MentorSessionTalentViewSerializer(sessions, many=True).data,
            status=status.HTTP_200_OK,
        )


# =============================================================================
# TALENT SIDE: CRUD own activities
# =============================================================================

class TalentActivityListCreateView(APIView):
    """
    GET  /api/v1/talents/me/mentorships/<id>/activities/   — list activities
    POST /api/v1/talents/me/mentorships/<id>/activities/   — talent self-logs
    """

    def get(self, request, mentorship_id):
        talent = _require_talent_profile(request.user)
        rel = _get_talent_relationship(talent, mentorship_id)
        activities = MenteeActivity.objects.filter(relationship=rel)
        return Response(
            MenteeActivitySerializer(activities, many=True).data,
            status=status.HTTP_200_OK,
        )

    def post(self, request, mentorship_id):
        talent = _require_talent_profile(request.user)
        rel = _get_talent_relationship(talent, mentorship_id)
        serializer = MenteeActivityCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        activity = MenteeActivity.objects.create(relationship=rel, **serializer.validated_data)
        return Response(
            MenteeActivitySerializer(activity).data,
            status=status.HTTP_201_CREATED,
        )


class TalentActivityDetailView(APIView):
    """
    PATCH  /api/v1/talents/me/activities/<id>/   — update own log
    DELETE /api/v1/talents/me/activities/<id>/   — delete own log
    """

    def _get_activity(self, user, activity_id):
        talent = _require_talent_profile(user)
        try:
            activity = MenteeActivity.objects.select_related('relationship').get(pk=activity_id)
        except MenteeActivity.DoesNotExist:
            raise NotFound('Activity not found.')
        if activity.relationship.talent_id != talent.id:
            raise PermissionDenied('You do not own this activity.')
        return activity

    def patch(self, request, activity_id):
        activity = self._get_activity(request.user, activity_id)
        serializer = MenteeActivityUpdateSerializer(activity, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(MenteeActivitySerializer(activity).data, status=status.HTTP_200_OK)

    def delete(self, request, activity_id):
        activity = self._get_activity(request.user, activity_id)
        activity.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
