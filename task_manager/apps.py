from django.apps import AppConfig


class TaskManagerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "task_manager"

    def ready(self):
        from . import signals
        from . import handlers
