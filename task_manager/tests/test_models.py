from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.text import slugify

from task_manager.models import (
    Position,
    Team,
    Project,
    Tag,
    TaskType,
    Task,
    NotificationType,
    Notification
)

POSITION_NAME = "Tester"
WORKER_USERNAME = "test.username"
WORKER_FIRST_NAME = "test_first"
WORKER_LAST_NAME = "test_last"
WORKER_PASSWORD = "test_password"
TEAM_NAME = "Flaming Testers"
TEAM_SLUG = "flaming_testers"
PROJECT_NAME = "Test project"
PROJECT_SLUG = "test_project"
TAG_NAME = "test_tag"
TASK_TYPE_NAME = "test_task"
TASK_ID = 1
TASK_NAME = "Test task"
NOTIFICATION_TYPE_NAME = "test_message"
NOTIFICATION_TYPE_MESSAGE_TEMPLATE = ("Message about task \"{task.name}\" "
                                      "from {task.requester}")
NOTIFICATION_SENT_AT = datetime(2020, 2, 2, 22, 22, 22)


class ModelsTests(TestCase):
    @staticmethod
    def load_test_position():
        position = Position.objects.get_or_create(
            id=1,
            name=POSITION_NAME
        )[0]
        return position

    def load_test_worker(self):
        position = self.load_test_position()
        worker = get_user_model().objects.create_user(
            id=1,
            position=position,
            username=WORKER_USERNAME,
            password=WORKER_PASSWORD,
        )
        return worker

    def load_test_team(self):
        worker = self.load_test_worker()
        team = Team.objects.get_or_create(
            id=1,
            name=TEAM_NAME,
            slug=TEAM_SLUG
        )[0]
        team.members.add(worker)
        return team

    def load_test_project(self):
        team = self.load_test_team()
        project = Project.objects.get_or_create(
            id=1,
            name=PROJECT_NAME,
            slug=PROJECT_SLUG,
            working_team=team
        )[0]
        return project

    @staticmethod
    def load_test_tag():
        tag = Tag.objects.get_or_create(
            id=1,
            name=TAG_NAME
        )[0]
        return tag

    @staticmethod
    def load_test_task_type():
        task_type = TaskType.objects.get_or_create(
            id=1,
            name=TASK_TYPE_NAME
        )[0]
        return task_type

    def load_test_task(self):
        project = self.load_test_project()
        worker = self.load_test_worker()
        tag = self.load_test_tag()
        task_type = self.load_test_task_type()
        task = Task.objects.get_or_create(
            id=TASK_ID,
            name=TASK_NAME,
            task_type=task_type,
            project=project,
            requester=worker
        )[0]
        task.tags.add(tag)
        task.assignees.add(worker)
        return task

    @staticmethod
    def load_test_notification_type():
        notification_type = NotificationType.objects.get_or_create(
            id=1,
            name=NOTIFICATION_TYPE_NAME,
            message_template=NOTIFICATION_TYPE_MESSAGE_TEMPLATE
        )[0]
        return notification_type

    def load_test_notification(self):
        user = self.load_test_worker()
        notification_type = self.load_test_notification_type()
        task = self.load_test_task()
        notification = Notification.objects.get_or_create(
            id=1,
            user=user,
            notification_type=notification_type,
            task=task,
            sent_at=NOTIFICATION_SENT_AT,
        )[0]
        return notification

    def test_position_str(self):
        position = self.load_test_position()
        self.assertEquals(str(position), POSITION_NAME)

    def test_create_worker_with_position(self):
        position = self.load_test_position()
        worker = self.load_test_worker()
        self.assertEquals(worker.position, position)
        self.assertEquals(worker.username, WORKER_USERNAME)
        self.assertTrue(worker.check_password(WORKER_PASSWORD))

    def test_worker_str(self):
        position = self.load_test_position()
        worker = self.load_test_worker()
        self.assertEquals(
            str(worker),
            f"{position}: {WORKER_FIRST_NAME} {WORKER_LAST_NAME}"
        )

    def test_create_team_without_slug(self):
        team = Team.objects.create(name=TEAM_NAME)
        self.assertEquals(team.slug, slugify(TEAM_NAME))

    def test_team_str(self):
        team = self.load_test_team()
        self.assertEquals(str(team), TEAM_NAME)

    def test_create_project_without_slug(self):
        team = self.load_test_team()
        project = Project(
            name=PROJECT_NAME,
            working_team=team,
        )
        self.assertEquals(project.slug, slugify(PROJECT_NAME))

    def test_project_str(self):
        project = self.load_test_project()
        self.assertEquals(str(project), PROJECT_NAME)

    def test_project_absolute_url(self):
        project = self.load_test_project()
        self.assertEquals(
            project.get_absolute_url(),
            f"/{TEAM_SLUG}/{PROJECT_SLUG}/")

    def test_tag_str(self):
        tag = self.load_test_tag()
        self.assertEquals(str(tag), TAG_NAME)

    def test_task_type_str(self):
        task_type = self.load_test_task_type()
        self.assertEquals(str(task_type), TASK_TYPE_NAME)

    def test_task_absolute_url(self):
        task = self.load_test_task()
        self.assertEquals(
            task.get_absolute_url(),
            f"/{TEAM_SLUG}/{PROJECT_SLUG}/task/{TASK_ID}")

    def test_task_get_priority_display(self):
        task = self.load_test_task()
        task.priority = task.Priority.OPTIONAL
        task.save()
        self.assertEquals(task.get_priority_display(), "Optional")

    def test_task_str(self):
        task = self.load_test_task()
        self.assertEquals(str(task), TASK_NAME)

    def test_notification_type_str(self):
        notification_type = self.load_test_notification_type()
        self.assertEquals(str(notification_type), NOTIFICATION_TYPE_NAME)

    def test_notification_str(self):
        notification = self.load_test_notification()
        notification_string = (
            f"{NOTIFICATION_TYPE_NAME}: "
            f"{TASK_NAME}, "
            f"{NOTIFICATION_SENT_AT.strftime('%d.%m.%Y %H:%M:%S')}"
        )
        self.assertEquals(str(notification), notification_string)

    def test_notification_get_message_text(self):
        task = self.load_test_task()
        notification = self.load_test_notification()
        message_text = NOTIFICATION_TYPE_MESSAGE_TEMPLATE.format(task=task)
        self.assertEquals(notification.message_text, message_text)
