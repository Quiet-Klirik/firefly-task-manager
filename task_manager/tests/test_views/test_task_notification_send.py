import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from task_manager.models import Team, Project, TaskType, Task
from task_manager.tests.test_views.utils import assert_url_access


TASK_REQUEST_REVIEW_URL_NAME = "task_manager:task-request-review"
TASK_MARK_AS_COMPLETED_URL_NAME = "task_manager:task-mark-as-completed"


class PublicTaskNotificationSendTests(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(name="Test team")
        self.project = Project.objects.create(
            name="Test project",
            working_team=self.team,
        )
        self.task_type = TaskType.objects.create(name="Test TaskType")
        self.task = Task.objects.create(
            name="Test task",
            project=self.project,
            deadline=datetime.date(2222, 2, 22),
            task_type=self.task_type
            )

    def test_task_request_review_login_required(self):
        assert_url_access(
            self,
            TASK_REQUEST_REVIEW_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_task_mark_as_completed_login_required(self):
        assert_url_access(
            self,
            TASK_MARK_AS_COMPLETED_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )


class PrivateTaskNotificationSendTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create(username="test.user")
        self.task_requester = get_user_model().objects.create(
            username="task.requester"
        )
        self.task_assignee = get_user_model().objects.create(
            username="task.assignee"
        )
        self.team = Team.objects.create(name="Private test team")
        self.project = Project.objects.create(
            name="Private test project",
            working_team=self.team,
        )
        self.task_type = TaskType.objects.create(name="Test TaskType")
        self.task = Task.objects.create(
            name="Test task",
            project=self.project,
            deadline=datetime.date(2222, 2, 22),
            task_type=self.task_type,
            requester=self.task_requester
            )
        self.task.assignees.add(self.task_assignee)

    def test_discard_task_request_review_page_for_not_assignee(self):
        self.client.force_login(self.user)
        assert_url_access(
            self,
            TASK_REQUEST_REVIEW_URL_NAME,
            403,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_discard_task_mark_as_completed_page_for_not_requester(self):
        self.client.force_login(self.task_assignee)
        assert_url_access(
            self,
            TASK_MARK_AS_COMPLETED_URL_NAME,
            403,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_redirect_task_request_review_page_for_assignee(self):
        self.client.force_login(self.task_assignee)
        assert_url_access(
            self,
            TASK_REQUEST_REVIEW_URL_NAME,
            302,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_redirect_task_mark_as_completed_page_for_requester(self):
        self.client.force_login(self.task_requester)
        assert_url_access(
            self,
            TASK_MARK_AS_COMPLETED_URL_NAME,
            302,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )
