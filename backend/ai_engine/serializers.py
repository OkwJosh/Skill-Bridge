from rest_framework import serializers


# =============================================================================
# Legacy: match-cv
# =============================================================================

class CVMatchRequestSerializer(serializers.Serializer):
    """Payload for POST /api/v1/ai/match-cv/."""

    name = serializers.CharField(max_length=200, required=False, allow_blank=True)
    skills = serializers.ListField(
        child=serializers.CharField(max_length=80),
        min_length=1,
        max_length=50,
    )
    experience = serializers.CharField(max_length=2000, required=False, allow_blank=True)

    def validate_skills(self, value):
        cleaned = [s.strip() for s in value if s and s.strip()]
        if not cleaned:
            raise serializers.ValidationError('At least one non-empty skill is required.')
        return cleaned


class CVMatchResponseSerializer(serializers.Serializer):
    matched_requirement_ids = serializers.ListField(child=serializers.CharField())
    matched_count = serializers.IntegerField()


# =============================================================================
# New Tier-1 features — response shapes are loose because payload comes from
# the LLM via services.py. We pass-through the cached dict and add a `cached`
# flag so the frontend can display "Last updated X ago".
# =============================================================================

class CachedInsightResponseSerializer(serializers.Serializer):
    """Generic envelope for any cached insight (trust, roadmap, curriculum)."""

    payload = serializers.JSONField()
    was_recomputed = serializers.BooleanField()
