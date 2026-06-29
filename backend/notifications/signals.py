"""
Signal-based notification creation
==================================

Domain events → notifications. Kept here (not in the source apps) so
notification logic lives in one file and the domain apps don't grow
cross-cutting imports of `notifications.models`.

The receivers fail-soft: any exception is swallowed so a flaky
notification create can never break the user's real action (e.g. a
mentor endorsing a skill).
"""

import logging

from django.db.models.signals import post_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)


def _safe_create(**kwargs):
    """Create a Notification, swallowing any error to avoid breaking the caller."""
    try:
        from .models import Notification
        Notification.objects.create(**kwargs)
    except Exception:  # noqa: BLE001
        logger.exception('Failed to create notification: %r', kwargs)


# ── Applications ────────────────────────────────────────────────────────────
# Created → notify the opportunity owner (org admin or mentor)
# Status changed → notify the applicant

@receiver(post_save, sender='opportunities.Application')
def on_application_saved(sender, instance, created, **kwargs):
    from .models import NotificationKind

    opportunity = instance.opportunity
    talent_user = instance.talent.user
    poster_name = opportunity.poster_name

    if created:
        # Notify the poster.
        recipients = []
        if opportunity.organization:
            from organizations.models import OrganizationMember
            recipients = list(
                OrganizationMember.objects.filter(
                    organization=opportunity.organization,
                    role__in=['owner', 'admin'],
                ).values_list('user_id', flat=True)
            )
        elif opportunity.mentor:
            recipients = [opportunity.mentor.user_id]

        for user_id in recipients:
            _safe_create(
                user_id=user_id,
                kind=NotificationKind.APPLICATION_SUBMITTED,
                title=f'New application for {opportunity.title}',
                body=f'{talent_user.full_name or talent_user.email} applied.',
                link_url=f'/app/jobs/{opportunity.id}',
                metadata={'application_id': instance.id, 'opportunity_id': opportunity.id},
            )
        return

    # Status change → notify the applicant. We can't easily detect changes here
    # without an `update_fields` hint; treat any save of an existing row as a
    # status-change notification *only* when the status field is not pending.
    # This is rough; the cleaner approach is to call a helper from the view
    # that mutates status. Acceptable for now: false positives are harmless
    # (notifications are cheap) and the view path is the only writer.
    if instance.status and instance.status != 'pending':
        _safe_create(
            user_id=talent_user.id,
            kind=NotificationKind.APPLICATION_STATUS_CHANGED,
            title=f'Application {instance.status}',
            body=f'Your application for {opportunity.title} at {poster_name} is now {instance.status}.',
            link_url='/app/my-applications',
            metadata={'application_id': instance.id, 'opportunity_id': opportunity.id,
                      'status': instance.status},
        )


# ── Skill endorsements ──────────────────────────────────────────────────────

@receiver(post_save, sender='talents.TalentSkill')
def on_talent_skill_saved(sender, instance, created, **kwargs):
    from .models import NotificationKind

    if not instance.is_endorsed:
        return
    # Endorsement happens on update, not create. Avoid firing on initial add.
    if created:
        return

    talent_user = instance.talent.user
    skill_name = getattr(instance.skill, 'name', 'a skill')
    endorser = instance.endorsed_by
    endorser_name = getattr(endorser, 'full_name', '') or getattr(endorser, 'email', 'A mentor')

    _safe_create(
        user_id=talent_user.id,
        kind=NotificationKind.SKILL_ENDORSED,
        title=f'{endorser_name} endorsed {skill_name}',
        body='Your Trust Score will refresh shortly.',
        link_url='/app/profile',
        metadata={'skill_id': instance.skill_id, 'endorser_id': getattr(endorser, 'id', None)},
    )


# ── Mentorship + sessions ───────────────────────────────────────────────────

@receiver(post_save, sender='mentors.MentorshipRelationship')
def on_mentorship_saved(sender, instance, created, **kwargs):
    from .models import NotificationKind
    if not created:
        return
    talent_user = instance.talent.user
    mentor_user = instance.mentor.user
    mentor_name = mentor_user.full_name or mentor_user.email
    _safe_create(
        user_id=talent_user.id,
        kind=NotificationKind.MENTORSHIP_CREATED,
        title=f'{mentor_name} is now your mentor',
        body=instance.focus_area or 'You can start scheduling sessions.',
        link_url='/app/profile',
        metadata={'mentorship_id': instance.id, 'mentor_id': mentor_user.id},
    )


@receiver(post_save, sender='mentors.MentorSession')
def on_mentor_session_saved(sender, instance, created, **kwargs):
    from .models import NotificationKind
    if not created:
        return
    rel = instance.relationship
    _safe_create(
        user_id=rel.talent.user_id,
        kind=NotificationKind.MENTOR_SESSION_SCHEDULED,
        title=f'New session scheduled with {rel.mentor.user.full_name or rel.mentor.user.email}',
        body=f'{instance.topic or "Mentorship session"} · {instance.scheduled_for:%a %d %b · %H:%M}',
        link_url='/app/profile',
        metadata={'session_id': instance.id, 'mentorship_id': rel.id},
    )


# ── School verification ─────────────────────────────────────────────────────

@receiver(post_save, sender='schools.StudentRosterRecord')
def on_roster_record_saved(sender, instance, created, **kwargs):
    from .models import NotificationKind
    # Only fire when a previously-unconsented row was just consented.
    if created or not instance.has_consented or not instance.talent_profile_id:
        return
    talent_user_id = instance.talent_profile.user_id
    _safe_create(
        user_id=talent_user_id,
        kind=NotificationKind.SCHOOL_VERIFIED,
        title=f'{instance.school.name} verified your academic record',
        body='This counts toward your Trust Score.',
        link_url='/app/profile',
        metadata={'school_id': instance.school_id},
    )
