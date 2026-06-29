"""
AI Engine service layer.

Wraps:
  - the standalone `ai_script/process_cv_supabase.py` (legacy match-cv endpoint)
  - new Tier-1 features: trust score, skill roadmap, project<->talent match,
    mentor<->mentee match, curriculum alignment

Conventions
-----------
* Every public function takes plain Python args (no Request, no view state)
  so it's testable and re-usable from management commands / Celery later.
* Every public function may raise: AIDisabledError, AITimeoutError, AIServiceError.
  Views map these to HTTP codes.
* LLM calls are wrapped in `_call_gemini_with_timeout` which inherits the
  same thread-pool timeout pattern as `match_cv_against_requirements`.
* Cached insights (trust score, skill roadmap, curriculum alignment) read
  through `get_or_recompute`.
"""

import json
import logging
import os
import sys
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError
from datetime import timedelta
from pathlib import Path
from typing import Callable, Optional

from django.conf import settings
from django.db.models import Count, Q
from django.utils import timezone

from .models import AIInsight
from .scoring import compute_trust_score


logger = logging.getLogger(__name__)


# =============================================================================
# Exceptions
# =============================================================================

class AIServiceError(Exception):
    """Generic AI failure (network, API key, Gemini-side error, Supabase error)."""


class AITimeoutError(AIServiceError):
    """AI call exceeded settings.AI_CALL_TIMEOUT_SECONDS."""


class AIDisabledError(AIServiceError):
    """GEMINI_API_KEY is not configured. Map to 503 ai_disabled in views."""


# =============================================================================
# Make `ai_script/` importable from inside Django (legacy match-cv path)
# =============================================================================

_AI_SCRIPT_DIR = Path(settings.BASE_DIR).parent / 'ai_script'
if str(_AI_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_SCRIPT_DIR))


# =============================================================================
# Shared infrastructure
# =============================================================================

def _timeout_seconds() -> int:
    return getattr(settings, 'AI_CALL_TIMEOUT_SECONDS', 30)


def assert_ai_available() -> None:
    """
    Raise AIDisabledError if the Gemini key is not configured.
    Called at the top of every view that depends on the LLM, so local devs
    without a key get a clean 503 with code 'ai_disabled' instead of a 500.
    """
    if not os.environ.get('GEMINI_API_KEY'):
        raise AIDisabledError('GEMINI_API_KEY is not set.')


def _get_gemini_client():
    """Lazy import + construct so missing google-genai doesn't crash Django boot."""
    assert_ai_available()
    try:
        from google import genai  # type: ignore
    except ImportError as exc:
        raise AIDisabledError(
            'google-genai is not installed. Run `pip install -r requirements.txt`.'
        ) from exc
    return genai.Client(api_key=os.environ['GEMINI_API_KEY'])


def _call_gemini_with_timeout(
    *, prompt: str, system_instruction: str, expect_json: bool = True,
):
    """
    Run a single Gemini call with the same hard-timeout pattern as match-cv.

    Returns:
        Parsed JSON dict if expect_json=True, else raw text string.
    """
    client = _get_gemini_client()

    def _do_call():
        from google.genai import types  # type: ignore
        model_name = getattr(settings, 'AI_GEMINI_MODEL', 'gemini-3-flash-preview')
        config_kwargs = {'system_instruction': system_instruction}
        if expect_json:
            config_kwargs['response_mime_type'] = 'application/json'
        response = client.models.generate_content(
            model=model_name,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        return response.text

    timeout = _timeout_seconds()
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(_do_call)
        try:
            raw = future.result(timeout=timeout)
        except FuturesTimeoutError as exc:
            raise AITimeoutError(f'AI call exceeded {timeout}s') from exc
        except Exception as exc:
            raise AIServiceError(str(exc)) from exc

    if not expect_json:
        return raw
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError) as exc:
        raise AIServiceError(f'Gemini returned non-JSON: {raw!r}') from exc


def get_or_recompute(
    *,
    subject_type: str,
    subject_id: int,
    kind: str,
    recompute_fn: Callable[[], dict],
    ttl_hours: int = 24,
    force_refresh: bool = False,
) -> tuple[dict, bool]:
    """
    Read cached insight from AIInsight, recompute if stale or missing or forced.

    Returns:
        (payload, was_recomputed)
    """
    cutoff = timezone.now() - timedelta(hours=ttl_hours)
    cached = AIInsight.objects.filter(
        subject_type=subject_type, subject_id=subject_id, kind=kind,
    ).first()

    if cached and not force_refresh and cached.recomputed_at >= cutoff:
        return cached.payload, False

    payload = recompute_fn()
    AIInsight.objects.update_or_create(
        subject_type=subject_type, subject_id=subject_id, kind=kind,
        defaults={'payload': payload},
    )
    return payload, True


# =============================================================================
# Legacy: wraps ai_script/process_cv_supabase.py
# =============================================================================

def match_cv_against_requirements(cv_data: dict) -> list:
    """
    Run the CV-matching pipeline against uncompared Supabase requirements.
    See `ai_script/process_cv_supabase.py` for the underlying script.
    """
    assert_ai_available()
    from process_cv_supabase import process_cv_comparison  # noqa: late import

    timeout = _timeout_seconds()
    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(process_cv_comparison, cv_data)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError as exc:
            raise AITimeoutError(f'AI matching exceeded {timeout}s') from exc
        except Exception as exc:
            raise AIServiceError(str(exc)) from exc


# =============================================================================
# Feature 1: Trust Score
# =============================================================================
#
# Pipeline: deterministic compute (scoring.py) → cache payload → LLM rationale.
# Rationale is a 2-sentence employer-facing explanation, NOT the score itself.

_TRUST_RATIONALE_SYSTEM = """
You are a hiring-platform trust analyst. Given a structured Trust Score
breakdown for a talent, produce a short employer-facing rationale (2 short
sentences, max 50 words). Output JSON: {"rationale": "..."}
Do not invent signals not present in the input. Do not restate the numeric
score. Focus on what employers should infer.
"""


def _trust_recompute_for_talent(talent_profile) -> dict:
    """Build the trust score payload for one TalentProfile."""
    from schools.models import StudentRosterRecord

    skills = list(talent_profile.skills.all())
    endorsed = sum(1 for s in skills if s.is_endorsed)

    # CGPA from any consenting roster record linked to this talent.
    cgpa = (
        StudentRosterRecord.objects
        .filter(talent_profile=talent_profile, has_consented=True, cgpa__isnull=False)
        .values_list('cgpa', flat=True)
        .first()
    )

    breakdown = compute_trust_score(
        endorsed_skill_count=endorsed,
        total_skill_count=len(skills),
        is_school_verified=talent_profile.is_school_verified,
        cgpa=cgpa,
        has_bio=bool(talent_profile.bio),
        has_headline=bool(talent_profile.headline),
        has_portfolio=bool(talent_profile.portfolio_url),
        has_github=bool(talent_profile.github_url),
        has_linkedin=bool(talent_profile.linkedin_url),
    )
    payload = breakdown.to_dict()

    # Best-effort LLM rationale. If the LLM is down, ship the score without it
    # rather than failing the whole request.
    try:
        rationale_resp = _call_gemini_with_timeout(
            prompt=json.dumps(payload),
            system_instruction=_TRUST_RATIONALE_SYSTEM,
        )
        payload['rationale'] = rationale_resp.get('rationale', '')
    except AIServiceError as exc:
        logger.warning('Trust rationale LLM call failed for talent_id=%s: %s',
                       talent_profile.id, exc)
        payload['rationale'] = ''

    return payload


def compute_trust_score_for_talent(talent_profile, force_refresh: bool = False) -> tuple[dict, bool]:
    """Public entry point. Returns (payload, was_recomputed)."""
    return get_or_recompute(
        subject_type=AIInsight.SUBJECT_TALENT,
        subject_id=talent_profile.id,
        kind=AIInsight.KIND_TRUST_SCORE,
        recompute_fn=lambda: _trust_recompute_for_talent(talent_profile),
        ttl_hours=24,
        force_refresh=force_refresh,
    )


# =============================================================================
# Feature 2: Skill Roadmap
# =============================================================================

_ROADMAP_SYSTEM = """
You are a career coach for early-career tech talents in Nigeria. Given a
talent's current skills (with proficiencies) and the aggregated demand
signals (most-requested skills they DON'T have, ranked), produce a 3-5
step learning roadmap. Each step must be actionable (a project, a course
type, or a guided project to seek out on the platform).

Output JSON:
{
  "summary": "1-sentence overview of the talent's biggest gap",
  "steps": [
    {"order": 1, "title": "...", "skill": "skill name", "rationale": "...", "suggested_action": "..."},
    ...
  ]
}
Do not invent skills outside the demand list.
"""


def _aggregate_market_demand(field_of_study: Optional[str], limit: int = 15) -> list[dict]:
    """
    Returns top N most-required skills across OPEN opportunities, optionally
    biased toward opportunities whose description contains field_of_study.

    Note: we don't have a CanonicalSkill <-> field-of-study mapping, so the
    field_of_study filter is best-effort text match on opportunity description.
    """
    from opportunities.models import Opportunity, OpportunityStatus

    qs = Opportunity.objects.filter(status=OpportunityStatus.OPEN)
    if field_of_study:
        qs = qs.filter(
            Q(description__icontains=field_of_study) |
            Q(title__icontains=field_of_study)
        )

    rows = (
        qs.values('required_skills__id', 'required_skills__name')
          .exclude(required_skills__id__isnull=True)
          .annotate(demand_count=Count('id'))
          .order_by('-demand_count')[:limit]
    )
    return [
        {'skill_id': r['required_skills__id'],
         'skill_name': r['required_skills__name'],
         'demand_count': r['demand_count']}
        for r in rows
    ]


def _roadmap_recompute_for_talent(talent_profile) -> dict:
    """Build skill roadmap payload."""
    own_skill_ids = set(talent_profile.skills.values_list('skill_id', flat=True))
    demand = _aggregate_market_demand(talent_profile.field_of_study)
    gaps = [d for d in demand if d['skill_id'] not in own_skill_ids]

    payload_base = {
        'current_skills': list(
            talent_profile.skills.values('skill__name', 'proficiency')
        ),
        'top_gaps': gaps[:8],
        'field_of_study': talent_profile.field_of_study or None,
    }

    if not gaps:
        # No gaps means either no demand data or talent already has everything.
        return {**payload_base, 'summary': 'No skill gaps detected from current market data.', 'steps': []}

    try:
        plan = _call_gemini_with_timeout(
            prompt=json.dumps(payload_base),
            system_instruction=_ROADMAP_SYSTEM,
        )
        return {**payload_base, 'summary': plan.get('summary', ''), 'steps': plan.get('steps', [])}
    except AIServiceError as exc:
        logger.warning('Roadmap LLM call failed for talent_id=%s: %s',
                       talent_profile.id, exc)
        # Fallback: list gaps without LLM narrative.
        return {
            **payload_base,
            'summary': 'AI narrative unavailable. Showing top market gaps.',
            'steps': [
                {'order': i + 1, 'title': f"Learn {g['skill_name']}",
                 'skill': g['skill_name'],
                 'rationale': f"Required in {g['demand_count']} open opportunity(ies).",
                 'suggested_action': ''}
                for i, g in enumerate(gaps[:5])
            ],
        }


def compute_skill_roadmap_for_talent(talent_profile, force_refresh: bool = False) -> tuple[dict, bool]:
    return get_or_recompute(
        subject_type=AIInsight.SUBJECT_TALENT,
        subject_id=talent_profile.id,
        kind=AIInsight.KIND_SKILL_ROADMAP,
        recompute_fn=lambda: _roadmap_recompute_for_talent(talent_profile),
        ttl_hours=24,
        force_refresh=force_refresh,
    )


# =============================================================================
# Feature 3: Project <-> Talent Match
# =============================================================================
# NOT cached — orgs expect fresh results when looking at their opportunity.

_PROJECT_MATCH_SYSTEM = """
You are an AI hiring assistant. Given an opportunity (title, description,
required skills) and a shortlist of talent candidates (each with their skill
list and headline), rank the candidates by fit. Consider skill overlap,
endorsement quality, and headline relevance.

Output JSON:
{
  "ranked": [
    {"talent_id": <int>, "rank": <int>, "fit_score": <0-100>, "reason": "1 short sentence"},
    ...
  ]
}
Return ALL candidates passed in, in ranked order. Do not invent talent_ids.
"""


def rank_talents_for_opportunity(opportunity, candidate_limit: int = 20) -> list[dict]:
    """
    Returns LLM-ranked talents for an opportunity. Pool is pre-filtered by
    Python (must share at least one required skill) and capped before the LLM.
    """
    from talents.models import TalentProfile

    required_skill_ids = list(opportunity.required_skills.values_list('id', flat=True))
    if not required_skill_ids:
        return []

    candidates = (
        TalentProfile.objects
        .filter(is_available=True, skills__skill_id__in=required_skill_ids)
        .distinct()
        .prefetch_related('skills__skill', 'user')[:candidate_limit]
    )

    if not candidates:
        return []

    candidate_payload = [
        {
            'talent_id': t.id,
            'headline': t.headline or '',
            'skills': [
                {'name': s.skill.name, 'proficiency': s.proficiency, 'endorsed': s.is_endorsed}
                for s in t.skills.all()
            ],
            'school_verified': t.is_school_verified,
        }
        for t in candidates
    ]

    prompt = json.dumps({
        'opportunity': {
            'title': opportunity.title,
            'description': opportunity.description[:1500],
            'required_skills': list(opportunity.required_skills.values_list('name', flat=True)),
            'experience_level': opportunity.experience_level,
        },
        'candidates': candidate_payload,
    })

    result = _call_gemini_with_timeout(prompt=prompt, system_instruction=_PROJECT_MATCH_SYSTEM)
    ranked = result.get('ranked', [])

    # Attach lightweight talent display info for the frontend.
    by_id = {t.id: t for t in candidates}
    enriched = []
    for r in ranked:
        t = by_id.get(r.get('talent_id'))
        if not t:
            continue
        enriched.append({
            **r,
            'talent': {
                'id': t.id,
                'full_name': getattr(t.user, 'full_name', '') or t.user.email,
                'headline': t.headline,
                'is_school_verified': t.is_school_verified,
            },
        })
    return enriched


# =============================================================================
# Feature 4: Mentor <-> Mentee Match
# =============================================================================
# NOT cached — mentor availability changes; talent gets fresh matches on demand.

_MENTOR_MATCH_SYSTEM = """
You are matching a learning talent with potential mentors. Given the
talent's current skills, top skill gaps, and a list of available mentors
with their expertise areas, rank the mentors by fit.

Prioritize mentors whose expertise covers the talent's GAPS (not skills they
already have). Output JSON:
{
  "ranked": [
    {"mentor_id": <int>, "rank": <int>, "fit_score": <0-100>, "reason": "..."}
  ]
}
Return all mentors passed in, in ranked order.
"""


def find_mentor_matches_for_talent(talent_profile, top_n: int = 5) -> list[dict]:
    from mentors.models import MentorProfile

    own_skill_ids = set(talent_profile.skills.values_list('skill_id', flat=True))

    # Roadmap insight (if cached) gives us the talent's gaps. Compute on the fly
    # otherwise — cheap aggregation, no LLM needed.
    cached_roadmap = AIInsight.objects.filter(
        subject_type=AIInsight.SUBJECT_TALENT,
        subject_id=talent_profile.id,
        kind=AIInsight.KIND_SKILL_ROADMAP,
    ).first()
    if cached_roadmap:
        gaps = cached_roadmap.payload.get('top_gaps', [])
    else:
        gaps = _aggregate_market_demand(talent_profile.field_of_study)
        gaps = [g for g in gaps if g['skill_id'] not in own_skill_ids][:8]

    gap_skill_ids = [g['skill_id'] for g in gaps]

    candidates = (
        MentorProfile.objects
        .filter(is_accepting_mentees=True)
        .filter(Q(expertise_areas__id__in=gap_skill_ids) if gap_skill_ids else Q())
        .distinct()
        .prefetch_related('expertise_areas', 'user')[:20]
    )
    if not candidates:
        return []

    candidate_payload = [
        {
            'mentor_id': m.id,
            'headline': m.headline or '',
            'expertise': list(m.expertise_areas.values_list('name', flat=True)),
            'is_verified': m.is_verified,
            'endorsements_given': m.endorsements_given,
        }
        for m in candidates
    ]
    prompt = json.dumps({
        'talent': {
            'skills': list(talent_profile.skills.values_list('skill__name', flat=True)),
            'field_of_study': talent_profile.field_of_study,
        },
        'gaps': [g['skill_name'] for g in gaps],
        'mentors': candidate_payload,
    })

    result = _call_gemini_with_timeout(prompt=prompt, system_instruction=_MENTOR_MATCH_SYSTEM)
    ranked = result.get('ranked', [])

    by_id = {m.id: m for m in candidates}
    enriched = []
    for r in ranked[:top_n]:
        m = by_id.get(r.get('mentor_id'))
        if not m:
            continue
        enriched.append({
            **r,
            'mentor': {
                'id': m.id,
                'full_name': getattr(m.user, 'full_name', '') or m.user.email,
                'headline': m.headline,
                'is_verified': m.is_verified,
                'expertise': list(m.expertise_areas.values_list('name', flat=True)),
            },
        })
    return enriched


# =============================================================================
# Feature 5: Curriculum Alignment (School)
# =============================================================================

_CURRICULUM_SYSTEM = """
You are an education-to-market analyst. Given a school's roster (departments,
courses, graduate counts) and the top in-demand skills from the platform's
opportunity pool, produce a curriculum alignment report.

Identify departments/courses whose graduates' claimed skills under-represent
in-demand skills. Output JSON:
{
  "summary": "2-sentence executive summary",
  "underrepresented_skills": [
    {"skill": "...", "market_demand": <int>, "current_graduates_with_skill": <int>, "recommendation": "..."}
  ],
  "well_aligned_departments": ["..."]
}
Only use data provided in the input.
"""


def _curriculum_recompute_for_school(school) -> dict:
    from schools.models import StudentRosterRecord
    from talents.models import TalentProfile

    # Roster summary: departments and how many graduates each has on the platform.
    roster = (
        StudentRosterRecord.objects
        .filter(school=school, has_consented=True)
        .values('department', 'course_of_study')
        .annotate(count=Count('id'))
    )

    # Skills currently held by this school's verified talents.
    verified_talents = TalentProfile.objects.filter(
        school_records__school=school, school_records__has_consented=True,
    ).distinct()
    talent_skill_counts = {}
    for t in verified_talents.prefetch_related('skills__skill'):
        for ts in t.skills.all():
            talent_skill_counts[ts.skill.name] = talent_skill_counts.get(ts.skill.name, 0) + 1

    market_demand = _aggregate_market_demand(field_of_study=None, limit=20)

    base = {
        'school_name': school.name,
        'departments': list(roster),
        'graduate_count': verified_talents.count(),
        'talent_skill_counts': talent_skill_counts,
        'market_demand': market_demand,
    }

    if not market_demand:
        return {**base, 'summary': 'No market demand data available yet.',
                'underrepresented_skills': [], 'well_aligned_departments': []}

    try:
        report = _call_gemini_with_timeout(
            prompt=json.dumps(base),
            system_instruction=_CURRICULUM_SYSTEM,
        )
        return {**base, **report}
    except AIServiceError as exc:
        logger.warning('Curriculum LLM call failed for school_id=%s: %s', school.id, exc)
        # Fallback: compute under-representation deterministically.
        underrep = []
        for d in market_demand[:10]:
            current = talent_skill_counts.get(d['skill_name'], 0)
            if current < d['demand_count']:
                underrep.append({
                    'skill': d['skill_name'],
                    'market_demand': d['demand_count'],
                    'current_graduates_with_skill': current,
                    'recommendation': '',
                })
        return {
            **base,
            'summary': 'AI narrative unavailable. Showing deterministic gap analysis.',
            'underrepresented_skills': underrep,
            'well_aligned_departments': [],
        }


# =============================================================================
# Feature 6: Predictive Talent Sourcing (Tier-2, low-confidence)
# =============================================================================
# Looks at the org's historical accepted/shortlisted applicants, builds a
# "successful applicant" profile, and surfaces similar talents who haven't
# applied yet. Confidence is honest: low when <5 past hires, medium otherwise.
# Not cached — org expects fresh results when looking at the dashboard.

_SOURCING_SYSTEM = """
You are an AI hiring assistant doing PROACTIVE talent sourcing. The
organization has a list of past successful applicants (their skills and
education backgrounds). You are also given a list of candidate talents who
have NOT yet applied to this org.

Rank candidates by how closely they resemble the pattern of past successes.
Be honest in `reason` — call out when confidence is low.

Output JSON:
{
  "ranked": [
    {"talent_id": <int>, "rank": <int>, "fit_score": <0-100>, "reason": "..."},
    ...
  ]
}
Return all candidates passed in, in ranked order.
"""


def predict_proactive_sourcing_for_org(organization, candidate_limit: int = 30) -> dict:
    """
    Returns a dict:
        {
          "confidence": "low" | "medium",
          "confidence_reason": "...",
          "past_hire_count": int,
          "matches": [...]
        }

    Pattern extraction is deterministic; ranking is LLM.
    """
    from opportunities.models import Application, ApplicationStatus
    from talents.models import TalentProfile

    successful = (
        Application.objects
        .filter(
            opportunity__organization=organization,
            status__in=[ApplicationStatus.ACCEPTED, ApplicationStatus.SHORTLISTED],
        )
        .select_related('talent')
        .prefetch_related('talent__skills__skill')
    )
    past_hire_count = successful.count()

    # Confidence is purely a function of sample size; expose it honestly.
    if past_hire_count == 0:
        return {
            'confidence': 'low',
            'confidence_reason': 'No past hires yet — cannot detect a pattern. Returning no matches.',
            'past_hire_count': 0,
            'matches': [],
        }
    confidence = 'medium' if past_hire_count >= 5 else 'low'
    confidence_reason = (
        f'Based on {past_hire_count} past hire(s). '
        f"Confidence will improve as you fill more opportunities."
    )

    # Extract the skill set across all successful hires.
    pattern_skill_ids = set()
    successful_profile = []
    for app in successful:
        talent_skill_names = []
        for ts in app.talent.skills.all():
            pattern_skill_ids.add(ts.skill_id)
            talent_skill_names.append(ts.skill.name)
        successful_profile.append({
            'education_route': app.talent.education_route,
            'school_verified': app.talent.is_school_verified,
            'skills': talent_skill_names,
        })

    # Find candidates: available, share ≥1 pattern skill, have NOT applied here.
    applied_talent_ids = (
        Application.objects
        .filter(opportunity__organization=organization)
        .values_list('talent_id', flat=True)
    )
    candidates = (
        TalentProfile.objects
        .filter(is_available=True, skills__skill_id__in=pattern_skill_ids)
        .exclude(id__in=applied_talent_ids)
        .distinct()
        .prefetch_related('skills__skill', 'user')[:candidate_limit]
    )
    if not candidates:
        return {
            'confidence': confidence,
            'confidence_reason': confidence_reason,
            'past_hire_count': past_hire_count,
            'matches': [],
        }

    candidate_payload = [
        {
            'talent_id': t.id,
            'headline': t.headline or '',
            'education_route': t.education_route,
            'school_verified': t.is_school_verified,
            'skills': [
                {'name': s.skill.name, 'endorsed': s.is_endorsed}
                for s in t.skills.all()
            ],
        }
        for t in candidates
    ]

    prompt = json.dumps({
        'organization_name': organization.name,
        'past_successful_applicants': successful_profile,
        'past_hire_count': past_hire_count,
        'confidence': confidence,
        'candidates': candidate_payload,
    })

    result = _call_gemini_with_timeout(prompt=prompt, system_instruction=_SOURCING_SYSTEM)
    ranked = result.get('ranked', [])

    by_id = {t.id: t for t in candidates}
    enriched = []
    for r in ranked:
        t = by_id.get(r.get('talent_id'))
        if not t:
            continue
        enriched.append({
            **r,
            'talent': {
                'id': t.id,
                'full_name': getattr(t.user, 'full_name', '') or t.user.email,
                'headline': t.headline,
                'is_school_verified': t.is_school_verified,
            },
        })

    return {
        'confidence': confidence,
        'confidence_reason': confidence_reason,
        'past_hire_count': past_hire_count,
        'matches': enriched,
    }


# =============================================================================
# Feature 7: Mentee Progress Insight (Tier-3, mentor-facing)
# =============================================================================
# Reads MentorshipRelationship + MentorSession + MenteeActivity to give the
# mentor a pre-session brief: where the mentee is excelling, where they're
# stuck, what changed since the last session.
# Not cached — mentor expects fresh insight every time they open it.

_PROGRESS_SYSTEM = """
You are a mentor's assistant. Given a mentor-mentee relationship, recent
mentee activity events, and prior session notes, produce a pre-session brief
for the mentor. Be specific, concrete, and short — the mentor reads this
2 minutes before the session.

Output JSON:
{
  "summary": "1-2 sentence headline",
  "wins": ["specific recent win", ...],
  "blockers": ["specific stuck point", ...],
  "suggested_topics": ["topic for this session", ...],
  "note_if_no_activity": null OR "string explaining"
}
If there is no activity, return note_if_no_activity and empty lists for the rest.
"""


def generate_mentee_progress_insight(relationship) -> dict:
    """
    Build a pre-session brief from the relationship's recent sessions + activity.

    Args:
        relationship: a mentors.MentorshipRelationship instance.
    """
    from mentors.models import MentorSession, MenteeActivity

    # Pull last 10 activities + last 3 completed sessions for context.
    activities = list(
        MenteeActivity.objects
        .filter(relationship=relationship)
        .order_by('-occurred_at')[:10]
        .values('activity_type', 'description', 'metadata', 'occurred_at')
    )
    recent_sessions = list(
        MentorSession.objects
        .filter(relationship=relationship, status=MentorSession.Status.COMPLETED)
        .order_by('-scheduled_for')[:3]
        .values('scheduled_for', 'topic', 'private_notes')
    )

    base = {
        'mentee_name': (
            getattr(relationship.talent.user, 'full_name', '') or relationship.talent.user.email
        ),
        'focus_area': relationship.focus_area,
        'relationship_started_at': relationship.started_at.isoformat(),
        'recent_activities': [
            {**a, 'occurred_at': a['occurred_at'].isoformat()} for a in activities
        ],
        'recent_sessions': [
            {**s, 'scheduled_for': s['scheduled_for'].isoformat()} for s in recent_sessions
        ],
    }

    if not activities and not recent_sessions:
        return {
            **base,
            'summary': 'No activity logged yet for this mentee.',
            'wins': [],
            'blockers': [],
            'suggested_topics': [],
            'note_if_no_activity': (
                'Encourage the mentee to log activity (skills added, projects shipped, '
                'blockers) so future briefs can be more specific.'
            ),
        }

    try:
        insight = _call_gemini_with_timeout(
            prompt=json.dumps(base),
            system_instruction=_PROGRESS_SYSTEM,
        )
        return {**base, **insight}
    except AIServiceError as exc:
        logger.warning('Progress insight LLM call failed for relationship_id=%s: %s',
                       relationship.id, exc)
        # Fallback: deterministic activity summary by type.
        from collections import Counter
        type_counts = Counter(a['activity_type'] for a in activities)
        wins = [a['description'] for a in activities
                if a['activity_type'] in ('project_shipped', 'application_accepted', 'skill_endorsed')][:3]
        blockers = [a['description'] for a in activities
                    if a['activity_type'] == 'blocker_reported'][:3]
        return {
            **base,
            'summary': (
                f'{len(activities)} recent activity event(s). '
                f'Most common: {type_counts.most_common(1)[0][0] if type_counts else "none"}.'
            ),
            'wins': wins,
            'blockers': blockers,
            'suggested_topics': [],
            'note_if_no_activity': 'AI narrative unavailable. Showing raw activity summary.',
        }


def compute_curriculum_alignment_for_school(school, force_refresh: bool = False) -> tuple[dict, bool]:
    return get_or_recompute(
        subject_type=AIInsight.SUBJECT_SCHOOL,
        subject_id=school.id,
        kind=AIInsight.KIND_CURRICULUM_ALIGNMENT,
        recompute_fn=lambda: _curriculum_recompute_for_school(school),
        ttl_hours=24,
        force_refresh=force_refresh,
    )
