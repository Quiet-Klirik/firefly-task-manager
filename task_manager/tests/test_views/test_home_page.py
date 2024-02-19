from django.test import TestCase

from django.urls import reverse

from task_manager.models import Team, Project, Worker
from .utils import assert_url_access


HOME_PAGE_URL = reverse("index")


class PublicHomePageTests(TestCase):
    def test_homepage_using_template(self):
        response = assert_url_access(self, HOME_PAGE_URL)
        self.assertTemplateUsed(response, "task_manager/index.html")

    # def test_homepage_context_data_consists_stats(self):
    #     response = self.client.get(HOME_PAGE_URL)
    #     context_data = response.context
    #     teams_count = Team.objects.count()
    #     projects_count = Project.objects.count()
    #     worker_count = Worker.objects.count()
    #     self.assertIn("teams_count", context_data)
    #     self.assertIn("projects_count", context_data)
    #     self.assertIn("workers_count", context_data)
    #     self.assertEquals(context_data["teams_count"], teams_count)
    #     self.assertEquals(context_data["projects_count"], projects_count)
    #     self.assertEquals(context_data["workers_count"], worker_count)
