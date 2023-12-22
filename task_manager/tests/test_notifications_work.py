from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TransactionTestCase

from task_manager.models import Team, Project, TaskType, Task, Notification


class NotificationsWorkTests(TransactionTestCase):
    def setUp(self) -> None:
        self.task_requester = get_user_model().objects.create(
            username="task.requester",
        )
        self.worker = get_user_model().objects.create(username="test.worker")
        self.team = Team.objects.create(name="Test team")
        self.team.members.add(self.worker)
        self.project = Project.objects.create(
            name="Test project",
            working_team=self.team
        )
        self.task_type = TaskType.objects.create(name="Test TaskType")
        with transaction.atomic():
            self.task = Task.objects.create(
                name="Test task",
                deadline=datetime(2020, 2, 4),
                task_type=self.task_type,
                project=self.project,
                requester=self.task_requester,
            )
            self.task.assignees.add(self.worker)

    def test_task_created_notification_is_creating(self):
        notification = Notification.objects.filter(
            user=self.worker,
            notification_type__name="task_created",
            task=self.task,
        )
        self.assertTrue(notification)

    def test_task_updated_notification_is_creating(self):
        self.task.description = "Some lorem ipsum text"
        self.task.save()
        notification = Notification.objects.filter(
            user=self.worker,
            notification_type__name="task_updated",
            task=self.task,
        )
        self.assertTrue(notification)

    def test_task_completed_notification_is_creating(self):
        self.task.mark_as_completed()
        notification = Notification.objects.filter(
            user=self.worker,
            notification_type__name="task_completed",
            task=self.task,
        )
        self.assertTrue(self.task.is_completed)
        self.assertTrue(notification)

    def test_task_review_requested_notification_is_creating(self):
        self.task.request_review()
        notification = Notification.objects.filter(
            user=self.task_requester,
            notification_type__name="task_review_requested",
            task=self.task,
        )
        self.assertTrue(notification)
