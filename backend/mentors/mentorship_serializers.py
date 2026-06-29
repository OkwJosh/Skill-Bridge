"""
Serializers for the mentorship subsystem:
  - MentorshipRelationship
  - MentorSession (separate mentor-view and talent-view variants — talents
    must NOT see `private_notes`)
  - MenteeActivity
"""

from rest_framework import serializers

from talents.models import TalentProfile

from .models import MentorshipRelationship, MentorSession, MenteeActivity


# =============================================================================
# Lightweight embedded representations
# =============================================================================

class _TalentMiniSerializer(serializers.Serializer):
    """Minimal talent identity for embedding in mentorship responses."""
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    headline = serializers.CharField(read_only=True)


class _MentorMiniSerializer(serializers.Serializer):
    """Minimal mentor identity for embedding."""
    id = serializers.IntegerField(read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    full_name = serializers.CharField(source='user.full_name', read_only=True)
    headline = serializers.CharField(read_only=True)
    is_verified = serializers.BooleanField(read_only=True)


# =============================================================================
# MentorshipRelationship
# =============================================================================

class MentorshipRelationshipSerializer(serializers.ModelSerializer):
    """Read serializer. Embeds both sides of the relationship."""
    mentor = _MentorMiniSerializer(read_only=True)
    talent = _TalentMiniSerializer(read_only=True)

    class Meta:
        model = MentorshipRelationship
        fields = ['id', 'mentor', 'talent', 'status', 'focus_area',
                  'started_at', 'ended_at']
        read_only_fields = fields


class MentorshipCreateSerializer(serializers.Serializer):
    """
    Mentor creates a relationship by passing a talent_profile_id.

    NOTE: this is a unilateral "mentor adds mentee" flow. A two-sided
    request/accept flow would add a PENDING status — out of scope here.
    """
    talent_profile_id = serializers.IntegerField()
    focus_area = serializers.CharField(max_length=255, required=False, allow_blank=True)

    def validate_talent_profile_id(self, value):
        if not TalentProfile.objects.filter(id=value).exists():
            raise serializers.ValidationError('Talent profile not found.')
        return value


class MentorshipUpdateSerializer(serializers.ModelSerializer):
    """Mentor edits status / focus_area. `status='ended'` sets ended_at."""
    class Meta:
        model = MentorshipRelationship
        fields = ['status', 'focus_area']


# =============================================================================
# MentorSession
# =============================================================================

class MentorSessionMentorViewSerializer(serializers.ModelSerializer):
    """
    Mentor-visible serializer. Includes `private_notes`.
    Used for: list/detail/create/update by mentor.
    """
    class Meta:
        model = MentorSession
        fields = ['id', 'relationship', 'scheduled_for', 'duration_minutes',
                  'status', 'topic', 'private_notes', 'created_at', 'updated_at']
        read_only_fields = ['id', 'relationship', 'created_at', 'updated_at']


class MentorSessionTalentViewSerializer(serializers.ModelSerializer):
    """
    Talent-visible serializer. `private_notes` is hidden.
    Used for: list/detail by talent.
    """
    class Meta:
        model = MentorSession
        fields = ['id', 'relationship', 'scheduled_for', 'duration_minutes',
                  'status', 'topic', 'created_at']
        read_only_fields = fields


class MentorSessionCreateSerializer(serializers.ModelSerializer):
    """Mentor creates a session within a known relationship (passed in URL)."""
    class Meta:
        model = MentorSession
        fields = ['scheduled_for', 'duration_minutes', 'status', 'topic', 'private_notes']
        extra_kwargs = {
            'status': {'required': False},
            'topic': {'required': False, 'allow_blank': True},
            'private_notes': {'required': False, 'allow_blank': True},
            'duration_minutes': {'required': False},
        }


# =============================================================================
# MenteeActivity
# =============================================================================

class MenteeActivitySerializer(serializers.ModelSerializer):
    """Read serializer. Visible to both sides of the relationship."""
    class Meta:
        model = MenteeActivity
        fields = ['id', 'relationship', 'activity_type', 'description',
                  'metadata', 'occurred_at', 'created_at']
        read_only_fields = ['id', 'relationship', 'created_at']


class MenteeActivityCreateSerializer(serializers.ModelSerializer):
    """Talent logs an activity. `relationship` is bound in the view from URL."""
    class Meta:
        model = MenteeActivity
        fields = ['activity_type', 'description', 'metadata', 'occurred_at']
        extra_kwargs = {
            'metadata': {'required': False},
        }


class MenteeActivityUpdateSerializer(serializers.ModelSerializer):
    """Talent edits their own log."""
    class Meta:
        model = MenteeActivity
        fields = ['activity_type', 'description', 'metadata', 'occurred_at']
        extra_kwargs = {
            'activity_type': {'required': False},
            'description': {'required': False},
            'metadata': {'required': False},
            'occurred_at': {'required': False},
        }
