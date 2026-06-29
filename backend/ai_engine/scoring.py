"""
Deterministic Trust Score math.

No AI. No external calls. Pure functions of TalentProfile + related rows.
Kept separate from services.py so it's trivially unit-testable and the
weights are auditable for employers.

Score is 0-100 with components:
    endorsements         (max 40) — verified skill endorsements from mentors
    school_verification  (max 25) — academic record verified by school admin
    academic_performance (max 15) — CGPA-derived
    profile_completeness (max 20) — bio, links, headline, skills present

A talent with no signal gets 0. A talent with strong signals on every
axis caps at 100.
"""

from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


# Maximum points per component — must sum to 100.
WEIGHTS = {
    'endorsements': 40,
    'school_verification': 25,
    'academic_performance': 15,
    'profile_completeness': 20,
}
assert sum(WEIGHTS.values()) == 100


@dataclass
class TrustScoreBreakdown:
    """Structured breakdown so the API response and the LLM rationale share the same numbers."""

    score: int
    components: dict = field(default_factory=dict)
    signals: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            'score': self.score,
            'components': self.components,
            'signals': self.signals,
            'weights': WEIGHTS,
        }


def _endorsement_points(endorsed_count: int, total_skills: int) -> tuple[int, dict]:
    """
    Up to 40 points. Saturates fast — 5 endorsements = full marks.
    Ratio gives partial credit when a talent has many skills but few endorsements.
    """
    if total_skills == 0:
        return 0, {'endorsed': 0, 'total': 0, 'ratio': 0.0}
    ratio = endorsed_count / total_skills
    # 8 points per endorsement up to 5, capped.
    raw = min(endorsed_count, 5) * 8
    return raw, {'endorsed': endorsed_count, 'total': total_skills, 'ratio': round(ratio, 2)}


def _school_verification_points(is_verified: bool) -> tuple[int, dict]:
    """Binary: 25 points if a school admin has verified academic records."""
    return (WEIGHTS['school_verification'] if is_verified else 0), {'verified': is_verified}


def _academic_performance_points(cgpa: Optional[Decimal]) -> tuple[int, dict]:
    """
    Up to 15 points. Linear scale on the standard 0.0-5.0 CGPA range.
    Returns 0 if CGPA is unknown (most common case — many schools opt out).
    """
    if cgpa is None:
        return 0, {'cgpa': None, 'note': 'not_provided'}
    cgpa_float = float(cgpa)
    if cgpa_float <= 0:
        return 0, {'cgpa': cgpa_float}
    # Map [0, 5] -> [0, 15]
    raw = min(15, int(round((cgpa_float / 5.0) * 15)))
    return raw, {'cgpa': cgpa_float}


def _profile_completeness_points(
    has_bio: bool,
    has_headline: bool,
    has_portfolio: bool,
    has_github: bool,
    has_linkedin: bool,
    skill_count: int,
) -> tuple[int, dict]:
    """
    Up to 20 points. 4 each for: bio, headline, github, linkedin, has-skills.
    Portfolio URL counts toward github if not set.
    """
    bits = {
        'bio': has_bio,
        'headline': has_headline,
        # Treat portfolio as a github fallback so self-taught talents aren't penalized.
        'github_or_portfolio': has_github or has_portfolio,
        'linkedin': has_linkedin,
        'has_skills': skill_count > 0,
    }
    raw = sum(4 for v in bits.values() if v)
    return raw, bits


def compute_trust_score(
    *,
    endorsed_skill_count: int,
    total_skill_count: int,
    is_school_verified: bool,
    cgpa: Optional[Decimal],
    has_bio: bool,
    has_headline: bool,
    has_portfolio: bool,
    has_github: bool,
    has_linkedin: bool,
) -> TrustScoreBreakdown:
    """
    Compute the deterministic 0-100 Trust Score.

    All inputs are explicit so this can be unit-tested without DB access.
    Callers (services.py) extract these from a TalentProfile + related rows.
    """
    endorse_pts,   endorse_sig   = _endorsement_points(endorsed_skill_count, total_skill_count)
    school_pts,    school_sig    = _school_verification_points(is_school_verified)
    academic_pts,  academic_sig  = _academic_performance_points(cgpa)
    profile_pts,   profile_sig   = _profile_completeness_points(
        has_bio=has_bio, has_headline=has_headline,
        has_portfolio=has_portfolio, has_github=has_github, has_linkedin=has_linkedin,
        skill_count=total_skill_count,
    )

    components = {
        'endorsements': endorse_pts,
        'school_verification': school_pts,
        'academic_performance': academic_pts,
        'profile_completeness': profile_pts,
    }
    score = sum(components.values())
    # Defensive cap (won't trigger with current weights, but protects against future tweaks).
    score = max(0, min(100, score))

    return TrustScoreBreakdown(
        score=score,
        components=components,
        signals={
            'endorsements': endorse_sig,
            'school_verification': school_sig,
            'academic_performance': academic_sig,
            'profile_completeness': profile_sig,
        },
    )
