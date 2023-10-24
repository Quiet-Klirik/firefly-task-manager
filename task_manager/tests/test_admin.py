from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Position


class AdminPageTests(TestCase):
    def setUp(self) -> None:
        self.default_position = Position.get_default_position()
        self.admin_user = get_user_model().objects.create_superuser(
            username="admin",
            password="admin_password",
            position=self.default_position
        )
        self.client.force_login(self.admin_user)
        position = Position.objects.create(name="Worker")
        self.worker = get_user_model().objects.create_user(
            username="office.worker",
            password="superhard_password",
            position=position,
        )

    def test_worker_position_listed(self):
        """
        Test that worker's position is in list_display
        on Worker admin page
        """
        url = reverse("admin:task_manager_worker_changelist")
        response = self.client.get(url)
        self.assertContains(response, self.worker.position)

    def test_worker_detail_position_listed(self):
        """
        Test that worker's position is on worker detail admin page
        """
        url = reverse(
            "admin:task_manager_worker_change",
            args=[self.worker.id]
        )
        response = self.client.get(url)
        self.assertContains(response, self.worker.position)
