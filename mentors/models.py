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

