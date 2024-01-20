from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.text import slugify
from taggit.managers import TaggableManager

from task_manager.signals import task_completed, task_review_requested


class Position(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    @classmethod
    def get_default_position(cls):
        default_position, created = cls.objects.get_or_create(name="User")
        return default_position

    def __str__(self):
        return self.name


class Worker(AbstractUser):
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="workers"
    )

    class Meta:
        ordering = ["position", "first_name", "last_name"]

    def get_absolute_url(self):
        return reverse("profile", kwargs={"slug": self.username})

    @classmethod
    def get_deleted_user(cls):
        try:
            deleted_user = cls.objects.get(username="deleted.user")
        except cls.DoesNotExist:
            deleted_user = cls.objects.create_user(
                username="deleted.user",
                first_name="deleted",
                last_name="user",
                password="admin_deleted_user_password"
            )
        return deleted_user

    def __str__(self):
        return f"{self.position}: {self.first_name} {self.last_name}"


class Team(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    founder = models.ForeignKey(
        Worker,
        on_delete=models.SET_NULL,
        null=True,
        related_name="founded_teams"
    )
    members = models.ManyToManyField(get_user_model(), related_name="teams")

    class Meta:
        ordering = ["name"]

    def get_absolute_url(self):
        return reverse(
            "task_manager:team-detail",
            kwargs={"team_slug": self.slug}
        )

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Team, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    def __str__(self):
        return self.name


class Project(models.Model):
    name = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    description = models.TextField(blank=True)
    working_team = models.ForeignKey(
        Team,
        on_delete=models.CASCADE,
        related_name="projects"
    )

    class Meta:
        ordering = ["name"]

    def save(
            self,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None
    ):
        if not self.slug:
            self.slug = slugify(self.name)
        super(Project, self).save(
            force_insert,
            force_update,
            using,
            update_fields
        )

    def get_absolute_url(self):
        return reverse(
            "task_manager:project-detail",
            kwargs={
                "team_slug": self.working_team.slug,
                "project_slug": self.slug
            }
        )

    def __str__(self):
        return self.name


class TaskType(models.Model):
    name = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Task(models.Model):
    class Priority(models.IntegerChoices):
        CRITICAL = 6, "Critical"
        URGENT = 5, "Urgent"
        HIGH = 4, "High"
        MIDDLE = 3, "Middle"
        LOW = 2, "Low"
        OPTIONAL = 1, "Optional"
        UNKNOWN = 0, "Unknown"
    name = models.CharField(max_length=255)
    tags = TaggableManager(related_name="tasks", blank=True)
    description = models.TextField(blank=True)
    deadline = models.DateField()
    is_completed = models.BooleanField(default=False)
    priority = models.PositiveSmallIntegerField(
        choices=Priority.choices,
        default=Priority.UNKNOWN
    )
    task_type = models.ForeignKey(TaskType, on_delete=models.CASCADE,)
    assignees = models.ManyToManyField(
        get_user_model(),
        related_name="assigned_tasks"
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    requester = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        related_name="requested_tasks"
    )

    class Meta:
        ordering = ["is_completed", "-priority", "name"]

    def get_priority_display(self):
        return self.Priority(self.priority).label

    def get_absolute_url(self):
        return reverse(
            "task_manager:task-detail",
            kwargs={
                "team_slug": self.project.working_team.slug,
                "project_slug": self.project.slug,
                "task_id": self.id
            }
        )

    def request_review(self):
        task_review_requested.send(sender=Task, instance=self)

    def mark_as_completed(self):
        self.is_completed = True
        self.save()
        task_completed.send(sender=Task, instance=self)

    def __str__(self):
        return self.name


class NotificationType(models.Model):
    name = models.CharField(max_length=255, unique=True)
    message_template = models.CharField(max_length=255, unique=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class Notification(models.Model):
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        related_name="notifications"
    )
    notification_type = models.ForeignKey(
        NotificationType,
        on_delete=models.CASCADE
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    sent_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-sent_at"]

    def mark_as_read(self):
        if self.is_read:
            return
        self.is_read = True
        self.save()

    @property
    def message_text(self) -> str:
        return self.notification_type.message_template.format(task=self.task)

    def __str__(self):
        return (f"{self.notification_type.name}: "
                f"{self.task.name}, "
                f"{self.sent_at.strftime('%d.%m.%Y %H:%M:%S')}")
