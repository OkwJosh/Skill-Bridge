"""
AI Engine API views.

Endpoints
---------
  POST /api/v1/ai/match-cv/                                 (legacy, kept)
  GET  /api/v1/ai/trust-score/me/                           Trust score for self
  GET  /api/v1/ai/trust-score/talents/<id>/                 Trust score for any talent
  GET  /api/v1/ai/skill-roadmap/me/                         Personalized roadmap
  GET  /api/v1/ai/opportunities/<id>/talent-matches/        Org owner ranks talents
  GET  /api/v1/ai/mentor-matches/                           Talent finds mentors
  GET  /api/v1/ai/schools/<id>/curriculum-alignment/        School analytics

Every view that depends on the LLM calls `assert_ai_available()` first so a
missing GEMINI_API_KEY returns 503 ai_disabled, not 500.
"""

import logging

from rest_framework import status
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .serializers import (
    CachedInsightResponseSerializer,
    CVMatchRequestSerializer,
    CVMatchResponseSerializer,
)
from .services import (
    AIDisabledError,
    AIServiceError,
    AITimeoutError,
    assert_ai_available,
    compute_curriculum_alignment_for_school,
    compute_skill_roadmap_for_talent,
    compute_trust_score_for_talent,
    find_mentor_matches_for_talent,
    generate_mentee_progress_insight,
    match_cv_against_requirements,
    predict_proactive_sourcing_for_org,
    rank_talents_for_opportunity,
)


logger = logging.getLogger(__name__)


# =============================================================================
# Shared helpers
# =============================================================================

def _error_envelope(*, http_status: int, error_type: str, code: str, message: str):
    """Build the standard {status:error, errors:[...]} envelope shape."""
    return Response(
        {
            'status': 'error',
            'data': None,
            'meta': {'http_status': http_status, 'error_type': error_type},
            'errors': [{'field': None, 'message': message, 'code': code}],
        },
        status=http_status,
    )


def _handle_ai_exception(exc: Exception, *, user_id) -> Response:
    """Map AIServiceError subclasses to HTTP responses."""
    if isinstance(exc, AIDisabledError):
        logger.info('AI request rejected (ai_disabled) for user_id=%s', user_id)
        return _error_envelope(
            http_status=503, error_type='AIDisabledError', code='ai_disabled',
            message='AI features are not configured on this server.',
        )
    if isinstance(exc, AITimeoutError):
        logger.warning('AI call timed out for user_id=%s: %s', user_id, exc)
        return _error_envelope(
            http_status=504, error_type='AITimeoutError', code='ai_timeout',
            message='The AI service took too long to respond. Please try again.',
        )
    logger.exception('AI call failed for user_id=%s', user_id)
    return _error_envelope(
        http_status=502, error_type='AIServiceError', code='ai_unavailable',
        message='AI service is currently unavailable.',
    )


def _wants_refresh(request) -> bool:
    return request.query_params.get('refresh', '').lower() in ('1', 'true', 'yes')


def _get_talent_profile_or_404(user):
    """Get the calling user's TalentProfile, 404 if they don't have one."""
    profile = getattr(user, 'talent_profile', None)
    if profile is None:
        raise NotFound('You do not have a talent profile.')
    return profile


# =============================================================================
# Legacy: match-cv
# =============================================================================

class MatchCVView(APIView):
    """POST /api/v1/ai/match-cv/  — accepts a CV payload, returns matching requirement IDs."""

    def post(self, request):
        request_serializer = CVMatchRequestSerializer(data=request.data)
        request_serializer.is_valid(raise_exception=True)
        cv_data = request_serializer.validated_data

        try:
            assert_ai_available()
            matched_ids = match_cv_against_requirements(cv_data)
        except AIServiceError as exc:
            return _handle_ai_exception(exc, user_id=request.user.id)

        response_serializer = CVMatchResponseSerializer({
            'matched_requirement_ids': matched_ids,
            'matched_count': len(matched_ids),
        })
        return Response(response_serializer.data, status=status.HTTP_200_OK)


# =============================================================================
# Trust Score
# =============================================================================

class TrustScoreMeView(APIView):
    """GET /api/v1/ai/trust-score/me/  — calling talent's own trust score."""

    def get(self, request):
        profile = _get_talent_profile_or_404(request.user)
        try:
            assert_ai_available()
            payload, was_recomputed = compute_trust_score_for_talent(
                profile, force_refresh=_wants_refresh(request),
            )
        except AIServiceError as exc:
            return _handle_ai_exception(exc, user_id=request.user.id)

        return Response(
            CachedInsightResponseSerializer(
                {'payload': payload, 'was_recomputed': was_recomputed}
            ).data,
            status=status.HTTP_200_OK,
        )


class TrustScoreForTalentView(APIView):
    """GET /api/v1/ai/trust-score/talents/<id>/  — read any talent's trust score."""

    def get(self, request, talent_id):
        from talents.models import TalentProfile

        try:
            profile = TalentProfile.objects.get(pk=talent_id)
        except TalentProfile.DoesNotExist:
            raise NotFound('Talent profile not found.')

        try:
            assert_ai_available()
            payload, was_recomputed = compute_trust_score_for_talent(
                profile, force_refresh=_wants_refresh(request),
            )
        except AIServiceError as exc:
            return _handle_ai_exception(exc, user_id=request.user.id)

        return Response(
            CachedInsightResponseSerializer(
                {'payload': payload, 'was_recomputed': was_recomputed}
            ).data,
            status=status.HTTP_200_OK,
        )


# =============================================================================
# Skill Roadmap
# =============================================================================

class SkillRoadmapMeView(APIView):
    """GET /api/v1/ai/skill-roadmap/me/  — calling talent's personalized roadmap."""

    def get(self, request):
        profile = _get_talent_profile_or_404(request.user)
        try:
            assert_ai_available()
            payload, was_recomputed = compute_skill_roadmap_for_talent(
                profile, force_refresh=_wants_refresh(request),
            )
        except AIServiceError as exc:
            return _handle_ai_exception(exc, user_id=request.user.id)

        return Response(
            CachedInsightResponseSerializer(
                {'payload': payload, 'was_recomputed': was_recomputed}
            ).data,
            status=status.HTTP_200_OK,
        )


# =============================================================================
# Project <-> Talent Match (Org)
# =============================================================================

class OpportunityTalentMatchesView(APIView):
    """
    GET /api/v1/ai/opportunities/<id>/talent-matches/

    Returns LLM-ranked talents for a given opportunity. Only the opportunity's
    creator (or org admin who owns it) may call this.
    """

    def get(self, request, opportunity_id):
        from opportunities.models import Opportunity

        try:
            opportunity = Opportunity.objects.get(pk=opportunity_id)
        except Opportunity.DoesNotExist:
            raise NotFound('Opportunity not found.')

        # Authorization: must have created the opportunity OR belong to the
        # posting organization OR be staff.
        is_creator = opportunity.created_by_id == request.user.id
        is_org_member = (
            opportunity.organization_id is not None
            and opportunity.organization.members.filter(user_id=request.user.id).exists()
        )
        if not (is_creator or is_org_member or request.user.is_staff):
            raise PermissionDenied('You do not own this opportunity.')

        try:
            assert_ai_available()
            ranked = rank_talents_for_opportunity(opportunity)
        except AIServiceError as exc:
            return _handle_ai_exception(exc, user_id=request.user.id)

        return Response(
            {'opportunity_id': opportunity.id, 'matches': ranked},
            status=status.HTTP_200_OK,
        )


# =============================================================================
# Mentor <-> Mentee Match
# =============================================================================

class MentorMatchesView(APIView):
    """GET /api/v1/ai/mentor-matches/  — calling talent's top mentor matches."""

    def get(self, request):
        profile = _get_talent_profile_or_404(request.user)
        try:
            assert_ai_available()
            matches = find_mentor_matches_for_talent(profile)
        except AIServiceError as exc:
            return _handle_ai_exception(exc, user_id=request.user.id)

        return Response({'matches': matches}, status=status.HTTP_200_OK)


# =============================================================================
# Curriculum Alignment (School)
# =============================================================================

# =============================================================================
# Predictive Talent Sourcing (Org)
# =============================================================================

class ProactiveSourcingView(APIView):
    """
    GET /api/v1/ai/organizations/<id>/proactive-sourcing/

    Surfaces talents who haven't applied but match the pattern of past
    successful hires. Org admin/member only.
    """

    def get(self, request, organization_id):
        from organizations.models import Organization

        try:
            organization = Organization.objects.get(pk=organization_id)
        except Organization.DoesNotExist:
            raise NotFound('Organization not found.')

        if not (organization.members.filter(user_id=request.user.id).exists()
                or request.user.is_staff):
            raise PermissionDenied('You are not a member of this organization.')

        try:
            assert_ai_available()
            payload = predict_proactive_sourcing_for_org(organization)
        except AIServiceError as exc:
            return _handle_ai_exception(exc, user_id=request.user.id)

        return Response({'organization_id': organization.id, **payload},
                        status=status.HTTP_200_OK)


# =============================================================================
# Mentee Progress Insight (Mentor)
# =============================================================================

class MenteeProgressInsightView(APIView):
    """
    GET /api/v1/ai/mentorships/<id>/progress-insight/

    Mentor-facing pre-session brief. Only the mentor in the relationship
    (or staff) may call this.
    """

    def get(self, request, mentorship_id):
        from mentors.models import MentorshipRelationship

        try:
            relationship = (
                MentorshipRelationship.objects
                .select_related('mentor__user', 'talent__user')
                .get(pk=mentorship_id)
            )
        except MentorshipRelationship.DoesNotExist:
            raise NotFound('Mentorship not found.')

        if not (relationship.mentor.user_id == request.user.id or request.user.is_staff):
            raise PermissionDenied('Only the mentor in this relationship may view this insight.')

        try:
            assert_ai_available()
            payload = generate_mentee_progress_insight(relationship)
        except AIServiceError as exc:
            return _handle_ai_exception(exc, user_id=request.user.id)

        return Response(
            {'mentorship_id': relationship.id, 'payload': payload},
            status=status.HTTP_200_OK,
        )


class CurriculumAlignmentView(APIView):
    """
    GET /api/v1/ai/schools/<id>/curriculum-alignment/

    School admin gets a market-alignment report for their school.
    """

    def get(self, request, school_id):
        from schools.models import School

        try:
            school = School.objects.get(pk=school_id)
        except School.DoesNotExist:
            raise NotFound('School not found.')

        # Authorization: must be a listed admin of this school.
        if not (school.admins.filter(pk=request.user.pk).exists() or request.user.is_staff):
            raise PermissionDenied('You are not an admin of this school.')

        try:
            assert_ai_available()
            payload, was_recomputed = compute_curriculum_alignment_for_school(
                school, force_refresh=_wants_refresh(request),
            )
        except AIServiceError as exc:
            return _handle_ai_exception(exc, user_id=request.user.id)

        return Response(
            CachedInsightResponseSerializer(
                {'payload': payload, 'was_recomputed': was_recomputed}
            ).data,
            status=status.HTTP_200_OK,
        )
