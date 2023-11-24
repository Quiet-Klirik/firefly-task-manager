from unittest.mock import Mock

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Team, Project, Worker

HOME_PAGE_URL = reverse("task_manager:index")
USER_REGISTER_URL = reverse("register")


def assert_login_required(test_case_obj: TestCase, url: str) -> None:
    response = test_case_obj.client.get(url)
    test_case_obj.assertNotEquals(response.status_code, 200)


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


class PublicUserTests(TestCase):
    def test_user_register_using_template(self):
        self.assertTemplateUsed = Mock()
        self.assertTemplateUsed.return_value = True

        response = self.client.get(USER_REGISTER_URL)
        self.assertEqual(response.status_code, 200)
        assert self.assertTemplateUsed(response, "registration/register.html")

    def assert_user_related_view_login_required(self, url_name: str) -> None:
        user = get_user_model().objects.create(username="test.user")
        url = reverse(url_name, kwargs={"slug": user.username})
        assert_login_required(self, url)

    def test_user_profile_login_required(self):
        self.assert_user_related_view_login_required("profile")


class PrivateUserTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.user",
            password="test_password"
        )
        self.client.force_login(self.user)

    def assert_retrieve_user_related_view(self, url_name: str) -> None:
        response = self.client.get(
            reverse(url_name, kwargs={"slug": self.user.username})
        )
        self.assertEquals(response.status_code, 200)

    def test_retrieve_user_profile_page(self):
        self.assert_retrieve_user_related_view("profile")
