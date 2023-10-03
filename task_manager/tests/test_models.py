from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils.text import slugify

from task_manager.models import Position, Worker, Team


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
