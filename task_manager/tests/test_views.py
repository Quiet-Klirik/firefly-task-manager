from unittest.mock import Mock

from django.test import TestCase
from django.urls import reverse

from task_manager.models import Team, Project, Worker

HOME_PAGE_URL = reverse("task_manager:index")
USER_REGISTER_URL = reverse("register")


class PublicHomePageTests(TestCase):
    def test_homepage_using_template(self):
        self.assertTemplateUsed = Mock()
        self.assertTemplateUsed.return_value = True

        response = self.client.get(HOME_PAGE_URL)
        self.assertEqual(response.status_code, 200)
        assert self.assertTemplateUsed(response, "task_manager/index.html")

    def test_homepage_context_data_consists_stats(self):
        response = self.client.get(HOME_PAGE_URL)
        context_data = response.context
        teams_count = Team.objects.count()
        projects_count = Project.objects.count()
        worker_count = Worker.objects.count()
        self.assertIn("teams_count", context_data)
        self.assertIn("projects_count", context_data)
        self.assertIn("workers_count", context_data)
        self.assertEquals(context_data["teams_count"], teams_count)
        self.assertEquals(context_data["projects_count"], projects_count)
        self.assertEquals(context_data["workers_count"], worker_count)


class UserRegisterViewTests(TestCase):
    def test_homepage_using_template(self):
        self.assertTemplateUsed = Mock()
        self.assertTemplateUsed.return_value = True

        response = self.client.get(USER_REGISTER_URL)
        self.assertEqual(response.status_code, 200)
        assert self.assertTemplateUsed(response, "registration/register.html")
