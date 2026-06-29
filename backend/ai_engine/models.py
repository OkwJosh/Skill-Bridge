"""
AI Engine models.

Single generic table for cached AI computations across all subject types
(talent, mentor, school, opportunity). Avoids polluting each domain
model with `ai_*` columns and lets us add new insight kinds without
schema migrations.
"""

from django.db import models


class AIInsight(models.Model):
    """
    A cached AI computation keyed by (subject_type, subject_id, kind).

    Examples:
        ('talent', 42, 'trust_score')         -> {'score': 78, 'components': {...}, 'rationale': '...'}
        ('talent', 42, 'skill_roadmap')       -> {'gaps': [...], 'plan': [...]}
        ('school', 7,  'curriculum_alignment')-> {'underrepresented': [...], 'summary': '...'}

    Read by views with `services.get_or_recompute(...)`; recomputed on
    staleness or when caller passes `?refresh=true`.
    """

    KIND_TRUST_SCORE = 'trust_score'
    KIND_SKILL_ROADMAP = 'skill_roadmap'
    KIND_CURRICULUM_ALIGNMENT = 'curriculum_alignment'
    # Project<->Talent and Mentor<->Mentee matches are intentionally NOT cached
    # — they depend on the live pool of opportunities/talents/mentors.

    KIND_CHOICES = [
        (KIND_TRUST_SCORE, 'Trust Score'),
        (KIND_SKILL_ROADMAP, 'Skill Roadmap'),
        (KIND_CURRICULUM_ALIGNMENT, 'Curriculum Alignment'),
    ]

    SUBJECT_TALENT = 'talent'
    SUBJECT_SCHOOL = 'school'

    SUBJECT_CHOICES = [
        (SUBJECT_TALENT, 'Talent'),
        (SUBJECT_SCHOOL, 'School'),
    ]

    subject_type = models.CharField(max_length=32, choices=SUBJECT_CHOICES, db_index=True)
    subject_id = models.PositiveIntegerField(db_index=True)
    kind = models.CharField(max_length=32, choices=KIND_CHOICES, db_index=True)

    payload = models.JSONField(help_text='The computed insight, shape depends on kind.')

    recomputed_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ai_insights'
        unique_together = [('subject_type', 'subject_id', 'kind')]
        indexes = [
            models.Index(fields=['subject_type', 'subject_id', 'kind']),
        ]
        verbose_name = 'AI Insight'
        verbose_name_plural = 'AI Insights'

    def __str__(self):
        return f'{self.kind} for {self.subject_type}#{self.subject_id}'
