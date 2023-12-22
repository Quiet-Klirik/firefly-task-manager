from django.contrib.auth import get_user_model
from django.test import TestCase

from task_manager.models import Team, Project
from .utils import assert_url_access


PROJECT_CREATE_URL_NAME = "task_manager:project-create"
PROJECT_DETAIL_URL_NAME = "task_manager:project-detail"
PROJECT_LANDING_URL_NAME = "task_manager:project-landing"
PROJECT_MEMBER_TASKS_URL_NAME = "task_manager:project-member-tasks"
PROJECT_UPDATE_URL_NAME = "task_manager:project-update"
PROJECT_DELETE_URL_NAME = "task_manager:project-delete"


class PublicProjectTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.user",
            password="test_password"
        )
        self.team = Team.objects.create(
            name="Test founded team",
            founder=self.user
        )
        self.project = Project.objects.create(
            name="Test founded project",
            working_team=self.team
        )

    def test_project_create_login_required(self):
        assert_url_access(
            self,
            PROJECT_CREATE_URL_NAME,
            200,
            False,
            team_slug=self.team.slug
        )

    def test_project_detail_login_required(self):
        assert_url_access(
            self,
            PROJECT_DETAIL_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_project_landing_template_used(self):
        response = assert_url_access(
            self,
            PROJECT_LANDING_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )
        self.assertTemplateUsed(response, "task_manager/project_landing.html")

    def test_project_member_tasks_login_required(self):
        assert_url_access(
            self,
            PROJECT_MEMBER_TASKS_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            user_slug=self.user.username
        )

    def test_project_update_login_required(self):
        assert_url_access(
            self,
            PROJECT_UPDATE_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_project_delete_login_required(self):
        assert_url_access(
            self,
            PROJECT_DELETE_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )


class UserProjectTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.user",
            password="user_password"
        )
        self.member = get_user_model().objects.create(username="member")
        self.team = Team.objects.create(
            name="Test team"
        )
        self.team.members.add(self.member)
        self.project = Project.objects.create(
            name="Test project",
            working_team=self.team
        )
        self.client.force_login(self.user)

    def test_discard_project_members_page_for_not_member(self):
        assert_url_access(
            self,
            PROJECT_DETAIL_URL_NAME,
            403,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_discard_project_member_tasks_page_for_not_member(self):
        assert_url_access(
            self,
            PROJECT_MEMBER_TASKS_URL_NAME,
            403,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            user_slug=self.member.username
        )


class TeamMemberProjectTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.member",
            password="member_password"
        )
        self.another_member = get_user_model().objects.create(
            username="another.member"
        )
        self.team = Team.objects.create(
            name="Involved team"
        )
        self.team.members.add(self.user, self.another_member)
        self.project = Project.objects.create(
            name="Involved project",
            working_team=self.team
        )
        self.client.force_login(self.user)

    def test_discard_project_create_page_for_not_founder(self):
        assert_url_access(
            self,
            PROJECT_CREATE_URL_NAME,
            403,
            team_slug=self.team.slug
        )

    def test_retrieve_project_members_page_for_member(self):
        assert_url_access(
            self,
            PROJECT_DETAIL_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_retrieve_project_member_tasks_page_template_used(self):
        response = assert_url_access(
            self,
            PROJECT_MEMBER_TASKS_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            user_slug=self.user.username
        )
        self.assertTemplateUsed(
            response,
            "task_manager/project_member_tasks.html"
        )

    def test_retrieve_project_member_tasks_page_for_member(self):
        assert_url_access(
            self,
            PROJECT_MEMBER_TASKS_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            user_slug=self.another_member.username
        )

    def test_discard_project_member_tasks_page_for_non_existent_member(self):
        not_involved_member = get_user_model().objects.create(
            username="not.involved.user"
        )
        assert_url_access(
            self,
            PROJECT_MEMBER_TASKS_URL_NAME,
            404,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            user_slug=not_involved_member.username
        )

    def test_discard_project_update_page_for_not_founder(self):
        assert_url_access(
            self,
            PROJECT_UPDATE_URL_NAME,
            403,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_discard_project_delete_page_for_not_founder(self):
        assert_url_access(
            self,
            PROJECT_DELETE_URL_NAME,
            403,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )


class TeamFounderProjectTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.founder",
            password="founder_password"
        )
        self.team = Team.objects.create(
            name="Founded team",
            founder=self.user
        )
        self.project = Project.objects.create(
            name="Founded project",
            working_team=self.team
        )
        self.client.force_login(self.user)

    def test_retrieve_project_create_page_for_founder(self):
        assert_url_access(
            self,
            PROJECT_CREATE_URL_NAME,
            team_slug=self.team.slug
        )

    def test_retrieve_project_update_page_for_founder(self):
        assert_url_access(
            self,
            PROJECT_UPDATE_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_retrieve_project_delete_page_for_founder(self):
        assert_url_access(
            self,
            PROJECT_DELETE_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )
