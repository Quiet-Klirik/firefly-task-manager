import datetime

from django.contrib.auth import get_user_model
from django.db import transaction
from django.test import TransactionTestCase

from task_manager.models import Team, Project, TaskType, Task, Notification
from task_manager.tests.test_views.utils import assert_url_access


NOTIFICATION_REDIRECT_URL_NAME = "task_manager:notification-redirect"


class NotificationRedirectTests(TransactionTestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create(username="test.user")
        self.another_user = get_user_model().objects.create(
            username="another.user"
        )
        self.team = Team.objects.create(name="Test team")
        self.project = Project.objects.create(
            name="Test Project",
            working_team=self.team,
        )
        self.task_type = TaskType.objects.create(name="Test TaskType")
        with transaction.atomic():
            self.task = Task.objects.create(
                name="Test task",
                project=self.project,
                deadline=datetime.date(2222, 2, 22),
                task_type=self.task_type
                )
            self.task.assignees.add(self.user)
        self.notification = Notification.objects.get(
            notification_type__name="task_created"
        )
        self.client.force_login(self.user)

    def test_notification_redirect_login_required(self):
        self.client.logout()
        assert_url_access(
            self,
            NOTIFICATION_REDIRECT_URL_NAME,
            200,
            False,
            id=self.notification.id
        )

    def test_discard_notification_redirect_page_for_not_receiver(self):
        self.client.logout()
        self.client.force_login(self.another_user)
        assert_url_access(
            self,
            NOTIFICATION_REDIRECT_URL_NAME,
            403,
            id=self.notification.id
        )

    def test_retrieve_notification_redirect_page_for_receiver(self):
        assert_url_access(
            self,
            NOTIFICATION_REDIRECT_URL_NAME,
            302,
            id=self.notification.id
        )
