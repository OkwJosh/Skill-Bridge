"""
Notification endpoints
======================

  GET  /api/v1/notifications/                 — paginated feed (?is_read=true/false)
  POST /api/v1/notifications/<id>/read/       — mark a single notification read
  POST /api/v1/notifications/read-all/        — mark all unread as read
  GET  /api/v1/notifications/unread-count/    — small endpoint for the bell badge
"""

from django.utils import timezone
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Notification
from .serializers import NotificationSerializer


class NotificationListView(APIView):
    """GET /api/v1/notifications/?is_read=true|false&limit=20"""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Notification.objects.filter(user=request.user).order_by('-created_at')

        is_read = request.query_params.get('is_read')
        if is_read is not None:
            qs = qs.filter(is_read=is_read.lower() == 'true')

        try:
            limit = max(1, min(100, int(request.query_params.get('limit', '50'))))
        except ValueError:
            limit = 50

        items = qs[:limit]
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({
            'items': NotificationSerializer(items, many=True).data,
            'unread_count': unread_count,
        })


class NotificationMarkReadView(APIView):
    """POST /api/v1/notifications/<id>/read/"""
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            note = Notification.objects.get(pk=pk, user=request.user)
        except Notification.DoesNotExist:
            return Response(
                {'status': 'error', 'data': None,
                 'meta': {'http_status': 404},
                 'errors': [{'field': None, 'message': 'Not found.', 'code': 'not_found'}]},
                status=status.HTTP_404_NOT_FOUND,
            )
        if not note.is_read:
            note.is_read = True
            note.read_at = timezone.now()
            note.save(update_fields=['is_read', 'read_at'])
        return Response(NotificationSerializer(note).data)


class NotificationMarkAllReadView(APIView):
    """POST /api/v1/notifications/read-all/"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        now = timezone.now()
        updated = Notification.objects.filter(
            user=request.user, is_read=False,
        ).update(is_read=True, read_at=now)
        return Response({'updated': updated})


class NotificationUnreadCountView(APIView):
    """GET /api/v1/notifications/unread-count/  — cheap badge endpoint."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        count = Notification.objects.filter(user=request.user, is_read=False).count()
        return Response({'unread_count': count})
