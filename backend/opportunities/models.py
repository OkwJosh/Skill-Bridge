"""
Opportunity Models for SkillBridge
==================================

Opportunities include internships, micro-projects, and guided projects.
Posted by Organizations or Mentors.
"""

from django.db import models
from django.conf import settings


class OpportunityType(models.TextChoices):
    """
    Types of opportunities available.

    SkillBridge is internship/project-based — not a general job board —
    so full-time / part-time employment listings are intentionally not
    offered. Any legacy rows of those types still display but can no
    longer be created or selected.
    """
    INTERNSHIP = 'internship', 'Internship'
    MICRO_PROJECT = 'micro_project', 'Micro-Project'
    GUIDED_PROJECT = 'guided_project', 'Guided Project'


class OpportunityStatus(models.TextChoices):
    """Status of an opportunity."""
    DRAFT = 'draft', 'Draft'
    OPEN = 'open', 'Open'
    CLOSED = 'closed', 'Closed'
    FILLED = 'filled', 'Filled'


class Opportunity(models.Model):
    """
    Job/project posting from an Organization or Mentor.
    """
    
    # Poster - can be an Organization OR a Mentor
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='opportunities'
    )
    
    mentor = models.ForeignKey(
        'mentors.MentorProfile',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='opportunities',
        help_text="For guided projects posted by mentors"
    )
    
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='opportunities_created'
    )
    
    # Basic Info
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()
    
    category = models.ForeignKey(
        'core.Category',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='opportunities'
    )
    
    opportunity_type = models.CharField(
        max_length=20,
        choices=OpportunityType.choices,
        default=OpportunityType.INTERNSHIP,
        db_index=True
    )
    
    status = models.CharField(
        max_length=20,
        choices=OpportunityStatus.choices,
        default=OpportunityStatus.DRAFT,
        db_index=True
    )
    
    # Requirements
    required_skills = models.ManyToManyField(
        'core.CanonicalSkill',
        blank=True,
        related_name='opportunities_requiring'
    )
    
    experience_level = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., Entry-level, 1-2 years"
    )
    
    # Location
    is_remote = models.BooleanField(default=False)
    location = models.CharField(max_length=200, blank=True)
    
    # Compensation
    is_paid = models.BooleanField(default=False)
    compensation = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., ₦150,000/month, $500 fixed"
    )
    
    # Duration
    duration = models.CharField(
        max_length=100,
        blank=True,
        help_text="e.g., 3 months, 2 weeks"
    )
    
    # Capacity
    max_applicants = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Maximum number of applications to accept"
    )
    
    spots_available = models.PositiveIntegerField(
        default=1,
        help_text="Number of positions available"
    )
    
    # Dates
    application_deadline = models.DateTimeField(null=True, blank=True)
    start_date = models.DateField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'opportunities'
        ordering = ['-created_at']
        verbose_name = 'Opportunity'
        verbose_name_plural = 'Opportunities'
    
    def __str__(self):
        poster = self.organization.name if self.organization else f"Mentor: {self.mentor.user.email}"
        return f"{self.title} ({poster})"
    
    @property
    def poster_name(self):
        """Return the name of whoever posted this opportunity."""
        if self.organization:
            return self.organization.name
        elif self.mentor:
            return self.mentor.user.full_name or self.mentor.user.email
        return "Unknown"


class ApplicationStatus(models.TextChoices):
    """Status of a talent's application."""
    PENDING = 'pending', 'Pending'
    REVIEWING = 'reviewing', 'Reviewing'
    SHORTLISTED = 'shortlisted', 'Shortlisted'
    INTERVIEW = 'interview', 'Interview'
    OFFERED = 'offered', 'Offered'
    ACCEPTED = 'accepted', 'Accepted'
    REJECTED = 'rejected', 'Rejected'
    WITHDRAWN = 'withdrawn', 'Withdrawn'


class Application(models.Model):
    """
    A Talent's application to an Opportunity.
    """
    
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='applications'
    )
    
    talent = models.ForeignKey(
        'talents.TalentProfile',
        on_delete=models.CASCADE,
        related_name='applications'
    )
    
    # Application Content
    cover_letter = models.TextField(
        blank=True,
        help_text="Why are you interested in this opportunity?"
    )
    
    resume_url = models.URLField(
        blank=True,
        help_text="Link to resume (can override profile resume)"
    )
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING,
        db_index=True
    )
    
    # Reviewer notes (internal)
    reviewer_notes = models.TextField(
        blank=True,
        help_text="Internal notes from reviewer"
    )
    
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='applications_reviewed'
    )
    
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'applications'
        ordering = ['-created_at']
        unique_together = ['opportunity', 'talent']  # One application per talent per opportunity
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
    
    def __str__(self):
        return f"{self.talent.user.email} -> {self.opportunity.title}"


class SavedOpportunity(models.Model):
    """
    Opportunities bookmarked/saved by a user.
    """
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_opportunities'
    )
    opportunity = models.ForeignKey(
        Opportunity,
        on_delete=models.CASCADE,
        related_name='saved_by_users'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'saved_opportunities'
        ordering = ['-created_at']
        unique_together = ['user', 'opportunity']
        verbose_name = 'Saved Opportunity'
        verbose_name_plural = 'Saved Opportunities'

    def __str__(self):
        return f"{self.user.email} saved {self.opportunity.title}"


class ApplicationInterview(models.Model):
    """
    Scheduled interviews for an application.
    """
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name='interviews'
    )
    round_name = models.CharField(
        max_length=100,
        help_text="e.g., Technical Interview, Culture Fit"
    )
    scheduled_at = models.DateTimeField()
    meeting_link = models.URLField(
        blank=True,
        help_text="Link to the video call"
    )
    notes = models.TextField(
        blank=True,
        help_text="Any additional instructions or notes for the talent"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'application_interviews'
        ordering = ['scheduled_at']
        verbose_name = 'Application Interview'
        verbose_name_plural = 'Application Interviews'

    def __str__(self):
        return f"{self.round_name} for {self.application}"
