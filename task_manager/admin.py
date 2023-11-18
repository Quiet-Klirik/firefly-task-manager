from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from task_manager.models import (
    Position,
    Worker,
    Team,
    Project,
    TaskType,
    Task,
    NotificationType,
    Notification
)

admin.site.register(Position)


@admin.register(Worker)
class WorkerAdmin(UserAdmin):
    list_display = UserAdmin.list_display + ("position",)
    list_filter = UserAdmin.list_filter + ("teams", "position",)
    fieldsets = UserAdmin.fieldsets + (
        ("Additional info", {"fields": ("position",)}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            "Additional info",
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "position",
                )
            }
        ),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ("name", "slug",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "working_team",)
    list_filter = ("working_team",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


admin.site.register(TaskType)


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("name", "task_type", "priority",
                    "is_completed", "deadline", "project")
    list_filter = ("tags", "task_type", "is_completed", "project",
                   "requester", "assignees")
    search_fields = ("name",)


@admin.register(NotificationType)
class NotificationTypeAdmin(admin.ModelAdmin):
    search_fields = ("name",)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("notification_type", "task", "sent_at", "user", "is_read")
    list_filter = ("user", "notification_type", "task")
