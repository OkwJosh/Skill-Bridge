"""
Mentor Models for SkillBridge
=============================

Mentors run guided projects and issue verified skill endorsements.
"""

from django.db import models
from django.conf import settings


class MentorProfile(models.Model):
    """
    Extended profile for mentors.
    
    Mentors can:
    - Run guided projects (via Opportunities)
    - Endorse talent skills
    - Provide endorsement notes
    """
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='mentor_profile'
    )
    
    # Professional Info
    headline = models.CharField(
        max_length=200,
        blank=True,
        help_text="Professional headline (e.g., 'Senior Software Engineer at Google')"
    )
    
    bio = models.TextField(
        blank=True,
        help_text="About the mentor - experience, expertise, mentoring style"
    )
    
    expertise_areas = models.ManyToManyField(
        'core.CanonicalSkill',
        blank=True,
        related_name='expert_mentors',
        help_text="Skills the mentor can endorse/teach"
    )
    
    # Professional Links
    linkedin_url = models.URLField(blank=True)
    website_url = models.URLField(blank=True)
    
    # Availability
    is_accepting_mentees = models.BooleanField(
        default=True,
        help_text="Currently accepting new mentees"
    )
    
    max_mentees = models.PositiveIntegerField(
        default=5,
        help_text="Maximum number of mentees at a time"
    )
    
    # Verification
    is_verified = models.BooleanField(
        default=False,
        help_text="Mentor credentials have been verified"
    )
    
    # Stats (denormalized for performance)
    endorsements_given = models.PositiveIntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'mentor_profiles'
        verbose_name = 'Mentor Profile'
        verbose_name_plural = 'Mentor Profiles'
    
    def __str__(self):
        return f"{self.user.email} - {self.headline or 'Mentor'}"


# =============================================================================
# MENTORSHIP RELATIONSHIPS
# =============================================================================
# Tracks active mentor<->talent pairings, individual sessions, and
# mentee activity events. The AI Engine reads these tables to produce
# Progress Insights before each mentor session.


class MentorshipRelationship(models.Model):
    """One mentor mentoring one talent. Multiple active relationships allowed."""

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        PAUSED = 'paused', 'Paused'
        ENDED = 'ended', 'Ended'

    mentor = models.ForeignKey(
        MentorProfile,
        on_delete=models.CASCADE,
        related_name='mentorships',
    )
    talent = models.ForeignKey(
        'talents.TalentProfile',
        on_delete=models.CASCADE,
        related_name='mentorships',
    )

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True,
    )

    # Free-text goal the talent + mentor agreed on at the start.
    focus_area = models.CharField(
        max_length=255, blank=True,
        help_text="What the mentee wants to learn (e.g. 'System design for backend roles')",
    )

    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'mentorship_relationships'
        unique_together = ['mentor', 'talent']
        ordering = ['-started_at']
        verbose_name = 'Mentorship Relationship'
        verbose_name_plural = 'Mentorship Relationships'

    def __str__(self):
        return f"{self.mentor.user.email} → {self.talent.user.email} ({self.status})"


class MentorSession(models.Model):
    """A single scheduled session between mentor and mentee."""

    class Status(models.TextChoices):
        SCHEDULED = 'scheduled', 'Scheduled'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'
        NO_SHOW = 'no_show', 'No Show'

    relationship = models.ForeignKey(
        MentorshipRelationship,
        on_delete=models.CASCADE,
        related_name='sessions',
    )

    scheduled_for = models.DateTimeField(db_index=True)
    duration_minutes = models.PositiveSmallIntegerField(default=30)

    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.SCHEDULED, db_index=True,
    )

    topic = models.CharField(max_length=255, blank=True)

    # Mentor's private post-session notes. Visible to the mentor only; the AI
    # Progress Insight may quote these but the talent does not see this field.
    private_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'mentor_sessions'
        ordering = ['-scheduled_for']
        verbose_name = 'Mentor Session'
        verbose_name_plural = 'Mentor Sessions'

    def __str__(self):
        return f"{self.relationship} @ {self.scheduled_for:%Y-%m-%d %H:%M}"


class MenteeActivity(models.Model):
    """
    An event in the mentee's learning life — surfaced to the mentor in
    Progress Insights so they walk into sessions knowing what changed.

    Sources: explicit log (mentee clicks 'I shipped X'), or system-generated
    (TalentSkill added → activity row, application accepted → activity row).
    """

    class ActivityType(models.TextChoices):
        SKILL_ADDED = 'skill_added', 'Skill Added'
        SKILL_ENDORSED = 'skill_endorsed', 'Skill Endorsed'
        APPLICATION_SUBMITTED = 'application_submitted', 'Application Submitted'
        APPLICATION_ACCEPTED = 'application_accepted', 'Application Accepted'
        PROJECT_SHIPPED = 'project_shipped', 'Project Shipped'
        BLOCKER_REPORTED = 'blocker_reported', 'Blocker Reported'
        NOTE = 'note', 'General Note'

    relationship = models.ForeignKey(
        MentorshipRelationship,
        on_delete=models.CASCADE,
        related_name='activities',
    )

    activity_type = models.CharField(
        max_length=32, choices=ActivityType.choices, db_index=True,
    )

    description = models.TextField()

    # Structured extras: {"skill_name": "Docker"} for skill_added, etc.
    metadata = models.JSONField(default=dict, blank=True)

    occurred_at = models.DateTimeField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'mentee_activities'
        ordering = ['-occurred_at']
        verbose_name = 'Mentee Activity'
        verbose_name_plural = 'Mentee Activities'

    def __str__(self):
        return f"{self.relationship.talent.user.email}: {self.activity_type} @ {self.occurred_at:%Y-%m-%d}"
