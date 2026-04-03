"""
Talent Profile Models for SkillBridge
=====================================

Single unified TalentProfile for ALL talent types:
- University students
- Polytechnic students
- Bootcamp graduates
- Self-taught developers

This follows the architectural constraint: "Do NOT split into separate models"
"""

from django.db import models
from django.conf import settings


class EducationRoute(models.TextChoices):
    """
    Education background of the talent.
    Used to categorize talents without creating separate tables.
    """
    UNIVERSITY = 'university', 'University'
    POLYTECHNIC = 'polytechnic', 'Polytechnic'
    BOOTCAMP = 'bootcamp', 'Bootcamp'
    SELF_TAUGHT = 'self_taught', 'Self-Taught'


class TalentProfile(models.Model):
    """
    Extended profile for talents (job seekers/opportunity hunters).
    
    One-to-One relationship with User model.
    Created when a user sets is_talent=True or completes onboarding.
    
    Contains:
    - Professional info (headline, bio)
    - Education background (with verification status)
    - Location
    - Portfolio links
    - Availability preferences
    """
    
    # =========================================================================
    # USER LINK
    # =========================================================================
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='talent_profile',
        help_text="The user this talent profile belongs to"
    )
    
    # =========================================================================
    # PROFESSIONAL INFO
    # =========================================================================
    
    headline = models.CharField(
        max_length=200,
        blank=True,
        help_text="Professional headline (e.g., 'Full Stack Developer | React & Django')"
    )
    
    bio = models.TextField(
        blank=True,
        help_text="About me section - skills, experience, goals"
    )
    
    # =========================================================================
    # EDUCATION BACKGROUND
    # =========================================================================
    
    education_route = models.CharField(
        max_length=20,
        choices=EducationRoute.choices,
        default=EducationRoute.SELF_TAUGHT,
        db_index=True,
        help_text="Primary education/training background"
    )
    
    institution_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Name of university, polytechnic, or bootcamp"
    )
    
    field_of_study = models.CharField(
        max_length=200,
        blank=True,
        help_text="Major/course of study (e.g., 'Computer Science')"
    )
    
    graduation_year = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text="Year of graduation (or expected)"
    )
    
    # =========================================================================
    # SCHOOL VERIFICATION (Data Trust Feature)
    # =========================================================================
    
    is_school_verified = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Academic records verified by a School Admin"
    )
    
    verified_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='verifications_made',
        help_text="School Admin who verified this profile"
    )
    
    verified_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the verification was completed"
    )
    
    # =========================================================================
    # LOCATION
    # =========================================================================
    
    city = models.CharField(
        max_length=100,
        blank=True,
        help_text="City of residence"
    )
    
    state = models.CharField(
        max_length=100,
        blank=True,
        help_text="State/region"
    )
    
    country = models.CharField(
        max_length=100,
        default='Nigeria',
        help_text="Country of residence"
    )
    
    # =========================================================================
    # PROFESSIONAL LINKS
    # =========================================================================
    
    portfolio_url = models.URLField(
        blank=True,
        help_text="Personal portfolio website"
    )
    
    linkedin_url = models.URLField(
        blank=True,
        help_text="LinkedIn profile URL"
    )
    
    github_url = models.URLField(
        blank=True,
        help_text="GitHub profile URL"
    )
    
    resume_url = models.URLField(
        blank=True,
        help_text="Resume/CV URL (stored in Supabase Storage)"
    )
    
    # =========================================================================
    # PREFERENCES
    # =========================================================================
    
    is_available = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Currently looking for opportunities"
    )
    
    preferred_industries = models.ManyToManyField(
        'core.CanonicalIndustry',
        blank=True,
        related_name='interested_talents',
        help_text="Industries the talent is interested in"
    )
    
    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'talent_profiles'
        verbose_name = 'Talent Profile'
        verbose_name_plural = 'Talent Profiles'
    
    def __str__(self):
        return f"{self.user.email} - {self.headline or 'No headline'}"
    
    @property
    def location(self) -> str:
        """Return formatted location string."""
        parts = [p for p in [self.city, self.state, self.country] if p]
        return ', '.join(parts) if parts else ''


class TalentSkill(models.Model):
    """
    Junction table linking TalentProfile to CanonicalSkill.
    
    Includes additional metadata:
    - Proficiency level (beginner to expert)
    - Years of experience
    - Whether it's a primary/highlighted skill
    - Mentor endorsement status
    """
    
    class ProficiencyLevel(models.TextChoices):
        """Self-assessed skill proficiency level."""
        BEGINNER = 'beginner', 'Beginner'
        INTERMEDIATE = 'intermediate', 'Intermediate'
        ADVANCED = 'advanced', 'Advanced'
        EXPERT = 'expert', 'Expert'
    
    # =========================================================================
    # RELATIONSHIPS
    # =========================================================================
    
    talent = models.ForeignKey(
        TalentProfile,
        on_delete=models.CASCADE,
        related_name='skills',
        help_text="The talent profile"
    )
    
    skill = models.ForeignKey(
        'core.CanonicalSkill',
        on_delete=models.CASCADE,
        related_name='talent_skills',
        help_text="The canonical skill"
    )
    
    # =========================================================================
    # SKILL DETAILS
    # =========================================================================
    
    proficiency = models.CharField(
        max_length=20,
        choices=ProficiencyLevel.choices,
        default=ProficiencyLevel.BEGINNER,
        help_text="Self-assessed proficiency level"
    )
    
    years_experience = models.PositiveSmallIntegerField(
        default=0,
        help_text="Years of experience with this skill"
    )
    
    is_primary = models.BooleanField(
        default=False,
        help_text="Highlight as a primary/main skill on profile"
    )
    
    # =========================================================================
    # MENTOR ENDORSEMENT
    # =========================================================================
    
    is_endorsed = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Skill has been endorsed/verified by a mentor"
    )
    
    endorsed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='skill_endorsements_given',
        help_text="Mentor who endorsed this skill"
    )
    
    endorsed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the endorsement was given"
    )
    
    endorsement_note = models.TextField(
        blank=True,
        help_text="Optional note from the mentor about this endorsement"
    )
    
    # =========================================================================
    # TIMESTAMPS
    # =========================================================================
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'talent_skills'
        unique_together = ['talent', 'skill']  # One entry per skill per talent
        verbose_name = 'Talent Skill'
        verbose_name_plural = 'Talent Skills'
        ordering = ['-is_primary', '-is_endorsed', 'skill__name']
    
    def __str__(self):
        endorsed = " ✓" if self.is_endorsed else ""
        return f"{self.talent.user.email} - {self.skill.name} ({self.proficiency}){endorsed}"

