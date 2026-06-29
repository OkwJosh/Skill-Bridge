from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    name = 'notifications'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        # Import signals so Django wires the receivers on app load.
        # Imported lazily to avoid AppRegistryNotReady during migrations.
        from . import signals  # noqa: F401
