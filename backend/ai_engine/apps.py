from django.apps import AppConfig
from django.db.models.signals import post_save


class AiEngineConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ai_engine'
    verbose_name = 'AI Engine'

    def ready(self):
        # Wire signal handlers that invalidate cached AIInsight rows on
        # changes to source data (skills, profile, roster consent).
        from talents.models import TalentProfile, TalentSkill
        from schools.models import StudentRosterRecord
        from .signals import (
            invalidate_on_roster_change,
            invalidate_on_talent_profile_change,
            invalidate_on_talent_skill_change,
        )

        post_save.connect(
            invalidate_on_talent_skill_change, sender=TalentSkill,
            dispatch_uid='ai_engine.invalidate_on_talent_skill_change',
        )
        post_save.connect(
            invalidate_on_talent_profile_change, sender=TalentProfile,
            dispatch_uid='ai_engine.invalidate_on_talent_profile_change',
        )
        post_save.connect(
            invalidate_on_roster_change, sender=StudentRosterRecord,
            dispatch_uid='ai_engine.invalidate_on_roster_change',
        )
