"""
Signal handlers that invalidate cached AIInsight rows when source data
changes. The next read will re-compute fresh insights.

Wired in apps.py:AiEngineConfig.ready() to avoid circular imports.
"""

from .models import AIInsight


def _invalidate_for_talent(talent_id: int, kinds: list[str]) -> None:
    AIInsight.objects.filter(
        subject_type=AIInsight.SUBJECT_TALENT,
        subject_id=talent_id,
        kind__in=kinds,
    ).delete()


def invalidate_on_talent_skill_change(sender, instance, **kwargs):
    """A skill added or endorsed changes both trust score AND market gap analysis."""
    _invalidate_for_talent(
        instance.talent_id,
        [AIInsight.KIND_TRUST_SCORE, AIInsight.KIND_SKILL_ROADMAP],
    )


def invalidate_on_talent_profile_change(sender, instance, **kwargs):
    """Profile edits (bio, links, school verification flag) affect trust score."""
    _invalidate_for_talent(instance.id, [AIInsight.KIND_TRUST_SCORE])


def invalidate_on_roster_change(sender, instance, **kwargs):
    """Consent given (or CGPA updated) on a linked roster row → recompute trust."""
    if instance.talent_profile_id and instance.has_consented:
        _invalidate_for_talent(
            instance.talent_profile_id,
            [AIInsight.KIND_TRUST_SCORE],
        )
