from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.text import slugify

from task_manager.models import Position, Worker, Team, Project, Tag, TaskType, \
    Task


class ModelsTests(TestCase):
    def test_position_str(self):
        name = "Tester"
        position = Position.objects.create(name=name)
        self.assertEquals(str(position), name)

    def test_create_worker_with_position(self):
        username = "test.username"
        password = "test_password"
        position = Position.objects.create(name="Tester")
        worker = get_user_model().objects.create_user(
            position=position,
            username=username,
            password=password,
        )
        self.assertEquals(worker.position, position)
        self.assertEquals(worker.username, username)
        self.assertTrue(worker.check_password(password))

    def test_worker_str(self):
        position = Position.objects.create(name="Tester")
        username = "test.username"
        first_name = "test_first"
        last_name = "test_last"
        password = "test_password"
        worker = Worker.objects.create(
            position=position,
            username=username,
            first_name=first_name,
            last_name=last_name,
            password=password,
        )
        self.assertEquals(str(worker), f"{position}: {first_name} {last_name}")

    def test_create_team_without_slug(self):
        name = "Flaming Testers"
        team = Team.objects.create(name=name)
        self.assertEquals(team.slug, slugify(name))

    def test_team_str(self):
        name = "Flaming Testers"
        team = Team.objects.create(
            name=name,
        )
        self.assertEquals(str(team), name)

    def test_create_project_without_slug(self):
        name = "Test project"
        team = Team.objects.create(name="Flaming Testers")
        project = Project(
            name=name,
            working_team=team,
        )
        self.assertEquals(project.slug, slugify(name))

    def test_project_str(self):
        name = "Test project"
        team = Team.objects.create(
            name="Flaming Testers",
        )
        project = Project.objects.create(
            name=name,
            working_team=team,
        )
        self.assertEquals(str(project), name)

    def test_project_absolute_url(self):
        team_slug = "flaming_testers"
        team = Team.objects.create(
            name="Flaming Testers",
            slug=team_slug,
        )
        project_slug = "test_project"
        project = Project.objects.create(
            name="Test project",
            slug=project_slug,
            working_team=team,
        )
        self.assertEquals(
            project.get_absolute_url(),
            f"/{team_slug}/{project_slug}/")

    def test_tag_str(self):
        name = "test_tag"
        tag = Tag.objects.create(name=name)
        self.assertEquals(str(tag), name)

    def test_task_type_str(self):
        name = "test_task"
        task_type = TaskType.objects.create(name=name)
        self.assertEquals(str(task_type), name)

    def test_task_absolute_url(self):
        task_type = TaskType.objects.create(name="test_task")
        team_slug = "flaming_testers"
        team = Team.objects.create(name="Flaming Testers", slug=team_slug)
        project_slug = "test_project"
        project = Project.objects.create(
            name="Test project",
            slug=project_slug,
            working_team=team
        )
        requester = Worker.objects.create(username="test.requester")
        task_id = 1
        name = "test_task"
        task = Task(
            id=task_id,
            name=name,
            task_type=task_type,
            project=project,
            requester=requester
        )
        self.assertEquals(
            task.get_absolute_url(),
            f"/{team_slug}/{project_slug}/task/{task_id}")

    @staticmethod
    def create_task_instance(name: str) -> Task:
        task_type = TaskType.objects.create(name="test_task")
        team = Team.objects.create(name="Flaming Testers")
        project = Project.objects.create(
            name="Test project",
            working_team=team
        )
        requester = Worker.objects.create(username="test.requester")
        task = Task(
            name=name,
            task_type=task_type,
            project=project,
            requester=requester
        )
        return task

    def test_task_get_priority_display(self):
        task = self.create_task_instance(name="test_task")
        task.priority = task.Priority.OPTIONAL
        task.save()
        self.assertEquals(task.get_priority_display(), "Optional")

    def test_task_str(self):
        name = "test_task"
        task = self.create_task_instance(name=name)
        self.assertEquals(str(task), name)
