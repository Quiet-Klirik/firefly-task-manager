import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import (
    Team,
    Project,
    TaskType,
    Task,
    NotificationType,
    Notification
)
from task_manager.tests.test_views.utils import assert_url_access, \
    assert_queryset_in_context

USER_PROFILE_URL_NAME = "profile"
TEAM_LIST_URL = reverse("task_manager:team-list")
TEAM_DETAIL_URL_NAME = "task_manager:team-detail"
PROJECT_DETAIL_URL_NAME = "task_manager:project-detail"
PROJECT_MEMBER_TASKS_URL_NAME = "task_manager:project-member-tasks"
TASK_DETAIL_URL_NAME = "task_manager:task-detail"


def sample_team(name: str, founder):
    return Team.objects.create(name=name, founder=founder)


def sample_project(name: str, team: Team):
    return Project.objects.create(name=name, working_team=team)


def sample_task(name: str, project: Project, user):
    task_type, _ = TaskType.objects.get_or_create(name="Test TaskType")
    task = Task.objects.create(
        name=name,
        project=project,
        deadline=datetime.date(2222, 2, 22),
        task_type=task_type,
        requester=user
    )
    task.assignees.add(user)
    return task


def sample_notification(task: Task):
    notification_type, _ = NotificationType.objects.get_or_create(
        name="test_notification",
    )
    user = task.assignees.first()
    return Notification.objects.create(
        user=user,
        notification_type=notification_type,
        task=task,
    )


class ViewsNotificationsContextTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(username="test.user")
        self.team1 = sample_team("Test team 1", self.user)
        self.team2 = sample_team("Test team 2", self.user)
        self.team1.members.add(self.user)
        self.team2.members.add(self.user)
        self.project1 = sample_project(
            name="Test project 1", team=self.team1
        )
        self.project2 = sample_project(
            name="Test project 2", team=self.team1
        )
        self.project3 = sample_project(
            name="Test project 3", team=self.team2
        )
        tasks = (
            sample_task("task1", self.project1, self.user),
            sample_task("task2", self.project1, self.user),
            sample_task("task3", self.project2, self.user),
            sample_task("task4", self.project3, self.user),
        )
        self.task1 = tasks[0]
        sample_notification(tasks[0])
        for task in tasks:
            sample_notification(task)
        self.client.force_login(self.user)

    def test_user_profile_page_consists_correct_notification_context(self):
        response = assert_url_access(
            self, USER_PROFILE_URL_NAME, slug=self.user.username,
        )
        context = response.context
        expected_notifications = self.user.notifications.all()
        assert_queryset_in_context(
            self, "notifications", expected_notifications, context
        )

    def test_team_list_page_consists_correct_notification_context(self):
        response = assert_url_access(
            self, TEAM_LIST_URL,
        )
        context = response.context
        expected_notifications = self.user.notifications.all()
        assert_queryset_in_context(
            self, "notifications", expected_notifications, context
        )

    def test_team_detail_page_consists_correct_notification_context(self):
        response1 = assert_url_access(
            self, TEAM_DETAIL_URL_NAME, team_slug=self.team1.slug,
        )
        response2 = assert_url_access(
            self, TEAM_DETAIL_URL_NAME, team_slug=self.team2.slug,
        )
        for response, team in (
                (response1, self.team1),
                (response2, self.team2)
        ):
            context = response.context
            expected_notifications = self.user.notifications.filter(
                task__project__working_team_id=team.id
            ).all()
            assert_queryset_in_context(
                self, "notifications", expected_notifications, context
            )

    def assert_correct_project_notifications(self, test_cases: tuple):
        for response, project in test_cases:
            context = response.context
            expected_notifications = self.user.notifications.filter(
                task__project_id=project.id
            ).all()
            self.assertIn("notifications", context)
            assert_queryset_in_context(
                self, "notifications", expected_notifications, context
            )

    def test_project_detail_page_consists_correct_notification_context(self):
        response1 = assert_url_access(
            self,
            PROJECT_DETAIL_URL_NAME,
            team_slug=self.team1.slug,
            project_slug=self.project1.slug,
        )
        response2 = assert_url_access(
            self,
            PROJECT_DETAIL_URL_NAME,
            team_slug=self.team1.slug,
            project_slug=self.project2.slug,
        )
        self.assert_correct_project_notifications((
            (response1, self.project1),
            (response2, self.project2),
            ))

    def test_project_member_tasks_page_consists_correct_notification_context(
            self
    ):
        response1 = assert_url_access(
            self,
            PROJECT_MEMBER_TASKS_URL_NAME,
            team_slug=self.team1.slug,
            project_slug=self.project1.slug,
            user_slug=self.user.username,
        )
        response2 = assert_url_access(
            self,
            PROJECT_MEMBER_TASKS_URL_NAME,
            team_slug=self.team1.slug,
            project_slug=self.project2.slug,
            user_slug=self.user.username,
        )
        self.assert_correct_project_notifications((
            (response1, self.project1),
            (response2, self.project2),
            ))

    def test_task_detail_page_consists_correct_notification_context(self):
        response = assert_url_access(
            self,
            TASK_DETAIL_URL_NAME,
            team_slug=self.team1.slug,
            project_slug=self.project1.slug,
            task_id=self.task1.id,
        )
        self.assert_correct_project_notifications((
            (response, self.project1),
        ))
