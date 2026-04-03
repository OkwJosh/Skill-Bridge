"""
Core Taxonomy Models for SkillBridge
====================================

Canonical tables for Skills and Industries.
These are the MASTER LISTS - all profiles and opportunities link to these.

Why Canonical Tables?
- Consistent data (no "Python" vs "python" vs "PYTHON")
- Better search and filtering
- Enables skill-based matching algorithms
- Supports auto-complete in frontend
"""

from django.db import models


class CanonicalSkill(models.Model):
    """
    Master list of skills in the platform.
    
    Examples: Python, React, Data Analysis, UI/UX Design, Project Management
    
    Talent profiles and opportunities link to this via Many-to-Many.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Skill name (e.g., 'Python', 'React', 'Data Analysis')"
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier"
    )
    
    category = models.CharField(
        max_length=100,
        blank=True,
        db_index=True,
        help_text="Skill category (e.g., 'Programming', 'Design', 'Marketing', 'Data')"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Optional description of the skill"
    )
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this skill is available for selection"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'canonical_skills'
        ordering = ['category', 'name']
        verbose_name = 'Skill'
        verbose_name_plural = 'Skills'
    
    def __str__(self):
        if self.category:
            return f"{self.name} ({self.category})"
        return self.name


class CanonicalIndustry(models.Model):
    """
    Master list of industries in the platform.
    
    Examples: FinTech, HealthTech, E-commerce, EdTech, AgriTech
    
    Organizations and opportunities link to this.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Industry name (e.g., 'FinTech', 'HealthTech', 'EdTech')"
    )
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        help_text="URL-friendly identifier"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Optional description of the industry"
    )
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this industry is available for selection"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'canonical_industries'
        ordering = ['name']
        verbose_name = 'Industry'
        verbose_name_plural = 'Industries'
    
    def __str__(self):
        return self.name

