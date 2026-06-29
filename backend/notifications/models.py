"""
Notification model
==================

A single, simple in-app feed per user. Notifications are created by
domain signals (see signals.py) and consumed by:

  GET  /api/v1/notifications/
  POST /api/v1/notifications/<id>/read/
  POST /api/v1/notifications/read-all/
  GET  /api/v1/notifications/unread-count/

`kind` tags the source so the UI can pick an icon / color. `metadata`
carries opaque structured extras (e.g. the application id) so the
frontend can route clicks without re-fetching half the world.
"""

from django.conf import settings
from django.db import models


class NotificationKind(models.TextChoices):
    APPLICATION_SUBMITTED = 'application_submitted', 'Application Submitted'
    APPLICATION_STATUS_CHANGED = 'application_status_changed', 'Application Status Changed'
    SKILL_ENDORSED = 'skill_endorsed', 'Skill Endorsed'
    MENTORSHIP_CREATED = 'mentorship_created', 'Mentorship Created'
    MENTOR_SESSION_SCHEDULED = 'mentor_session_scheduled', 'Mentor Session Scheduled'
    SCHOOL_VERIFIED = 'school_verified', 'School Verified'
    GENERIC = 'generic', 'Generic'


class Notification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
    )
    kind = models.CharField(
        max_length=40, choices=NotificationKind.choices,
        default=NotificationKind.GENERIC, db_index=True,
    )
    title = models.CharField(max_length=200)
    body = models.TextField(blank=True)
    # Where in the SPA to send the user when they click this notification.
    # Relative path (e.g. "/app/my-applications") — frontend handles routing.
    link_url = models.CharField(max_length=500, blank=True)
    # Structured extras for the frontend (application_id, opportunity_id, …).
    metadata = models.JSONField(default=dict, blank=True)

    is_read = models.BooleanField(default=False, db_index=True)
    read_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
        ]

    def __str__(self):
        return f'{self.user_id} · {self.kind} · {self.title[:30]}'
