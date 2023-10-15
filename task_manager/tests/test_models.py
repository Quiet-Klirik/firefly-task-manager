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
    NotificationType
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
NOTIFICATION_TYPE_MESSAGE_TEMPLATE = ("Message about task \"{task_name}\" "
                                      "from {receiver}")


class ModelsTests(TestCase):
    @staticmethod
    def load_test_position():
        position = Position.objects.create(name=POSITION_NAME)
        return position

    def load_test_worker(self):
        position = self.load_test_position()
        worker = get_user_model().objects.create_user(
            position=position,
            username=WORKER_USERNAME,
            password=WORKER_PASSWORD,
        )
        return worker

    def load_test_team(self):
        worker = self.load_test_worker()
        team = Team.objects.create(
            name=TEAM_NAME,
            slug=TEAM_SLUG
        )
        team.members.add(worker)
        return team

    def load_test_project(self):
        team = self.load_test_team()
        project = Project.objects.create(
            name=PROJECT_NAME,
            slug=PROJECT_SLUG,
            working_team=team
        )
        return project

    @staticmethod
    def load_test_tag():
        tag = Tag.objects.create(name=TAG_NAME)
        return tag

    @staticmethod
    def load_test_task_type():
        task_type = TaskType.objects.create(name=TASK_TYPE_NAME)
        return task_type

    def load_test_task(self):
        project = self.load_test_project()
        worker = self.load_test_worker()
        tag = self.load_test_tag()
        task_type = self.load_test_task_type()
        task = Task.objects.create(
            id=TASK_ID,
            name=TASK_NAME,
            task_type=task_type,
            project=project,
            requester=worker
        )
        task.tags.add(tag)
        task.assignees.add(worker)
        return task

    @staticmethod
    def load_test_notification_type():
        message_type = NotificationType.objects.create(
            name=NOTIFICATION_TYPE_NAME,
            message_template=NOTIFICATION_TYPE_MESSAGE_TEMPLATE
        )
        return message_type

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
