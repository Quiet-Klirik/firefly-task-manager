from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from task_manager.models import Team, Project, Worker

HOME_PAGE_URL = reverse("task_manager:index")
USER_REGISTER_URL = reverse("register")
USER_PROFILE_URL_NAME = "profile"
USER_PROFILE_REDIRECT_URL = reverse("profile-redirect")
USER_PROFILE_EDIT_URL = reverse("profile-edit")
USER_PROFILE_DELETE_URL = reverse("profile-delete")
TEAM_LIST_URL = reverse("task_manager:team-list")
TEAM_CREATE_URL = reverse("task_manager:team-create")
TEAM_DETAIL_URL_NAME = "task_manager:team-detail"
TEAM_UPDATE_URL_NAME = "task_manager:team-update"
TEAM_DELETE_URL_NAME = "task_manager:team-delete"
TEAM_KICK_MEMBER_URL_NAME = "task_manager:team-kick-member"
PROJECT_CREATE_URL_NAME = "task_manager:project-create"
PROJECT_DETAIL_URL_NAME = "task_manager:project-detail"
PROJECT_LANDING_URL_NAME = "task_manager:project-landing"
PROJECT_MEMBER_TASKS_URL_NAME = "task_manager:project-member-tasks"


def assert_url_access(
        self: TestCase,
        url_name: str,
        status_code: int = 200,
        must_equals: bool = True,
        **kwargs
):
    """:returns: response object"""
    if url_name.startswith("/"):
        url = url_name
    else:
        url = reverse(url_name, kwargs=kwargs)
    response = self.client.get(url)
    if must_equals:
        self.assertEquals(response.status_code, status_code)
    else:
        self.assertNotEquals(response.status_code, status_code)
    return response


class PublicHomePageTests(TestCase):
    def test_homepage_using_template(self):
        response = assert_url_access(self, HOME_PAGE_URL)
        self.assertTemplateUsed(response, "task_manager/index.html")

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
        response = assert_url_access(self, USER_REGISTER_URL)
        self.assertTemplateUsed(response, "registration/register.html")

    def assert_user_related_view_login_required(self, url_name: str) -> None:
        user = get_user_model().objects.create(username="test.user")
        assert_url_access(
            self,
            url_name,
            must_equals=False,
            slug=user.username
        )

    def test_user_profile_login_required(self):
        self.assert_user_related_view_login_required(USER_PROFILE_URL_NAME)

    def test_user_profile_redirect_login_required(self):
        assert_url_access(self, USER_PROFILE_REDIRECT_URL, 200, False)

    def test_user_profile_edit_login_required(self):
        assert_url_access(self, USER_PROFILE_EDIT_URL, 200, False)

    def test_user_profile_delete_login_required(self):
        assert_url_access(self, USER_PROFILE_DELETE_URL, 200, False)


class PrivateUserTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.user",
            password="test_password"
        )
        self.client.force_login(self.user)

    def assert_retrieve_user_related_view(self, url_name: str) -> None:
        assert_url_access(self, url_name, slug=self.user.username)

    def test_retrieve_user_profile_page(self):
        self.assert_retrieve_user_related_view(USER_PROFILE_URL_NAME)

    def test_redirect_user_profile_redirect_url(self):
        response = self.client.get(USER_PROFILE_REDIRECT_URL)
        expected_url = reverse(
            USER_PROFILE_URL_NAME,
            kwargs={"slug": self.user.username}
        )
        self.assertRedirects(response, expected_url)

    def test_retrieve_user_profile_edit_page(self):
        assert_url_access(self, USER_PROFILE_EDIT_URL)

    def test_user_profile_edit_object_is_current_user(self):
        response = assert_url_access(self, USER_PROFILE_EDIT_URL)
        context = response.context
        self.assertIn("object", context)
        self.assertEquals(context["object"], self.user)

    def test_retrieve_user_profile_delete(self):
        response = assert_url_access(self, USER_PROFILE_DELETE_URL)
        context_data = response.context
        self.assertIn("object", context_data)
        self.assertEquals(context_data["object"], self.user)


class PublicTeamTests(TestCase):
    def test_team_list_login_required(self):
        assert_url_access(self, TEAM_LIST_URL, 200, False)

    def test_team_create_login_required(self):
        assert_url_access(self, TEAM_CREATE_URL, 200, False)

    def assert_team_related_view_login_required(self, url_name: str) -> None:
        user = get_user_model().objects.create(username="test.user")
        team = Team.objects.create(name="Test team", founder=user)
        assert_url_access(self, url_name, 200, False, team_slug=team.slug)

    def test_team_detail_login_required(self):
        self.assert_team_related_view_login_required(
            TEAM_DETAIL_URL_NAME
        )

    def test_team_update_login_required(self):
        self.assert_team_related_view_login_required(
            TEAM_UPDATE_URL_NAME
        )

    def test_team_delete_login_required(self):
        self.assert_team_related_view_login_required(
            TEAM_DELETE_URL_NAME
        )

    def test_team_kick_member_login_required(self):
        user = get_user_model().objects.create(username="test.user")
        team = Team.objects.create(name="Test team", founder=user)
        team.members.add(user)
        team.save()
        assert_url_access(
            self,
            TEAM_KICK_MEMBER_URL_NAME,
            200,
            False,
            team_slug=team.slug,
            member_username=user.username
        )


class PrivateTeamTest(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.user",
            password="test_password"
        )
        self.founded_team = Team.objects.create(
            name="Test founded team",
            founder=self.user
        )
        self.involved_team = Team.objects.create(
            name="Test involved team",
            founder=get_user_model().objects.create(username="test.big.boss")
        )
        self.involved_team.members.add(self.user)
        self.involved_team.save()
        self.client.force_login(self.user)

    def test_retrieve_team_list_page(self):
        assert_url_access(self, TEAM_LIST_URL)

    def test_team_list_correct_context_data(self):
        response = self.client.get(TEAM_LIST_URL)
        context_data = response.context
        self.assertIn("involved_teams", context_data)
        self.assertIn("founded_teams", context_data)
        self.assertEquals(
            list(context_data["involved_teams"]),
            list(self.user.teams.all())
        )
        self.assertEquals(
            list(context_data["founded_teams"]),
            list(self.user.founded_teams.all())
        )

    def test_team_list_using_template(self):
        response = assert_url_access(self, TEAM_LIST_URL)
        self.assertTemplateUsed(response, "task_manager/team_list.html")

    def test_retrieve_team_create_page(self):
        assert_url_access(self, TEAM_CREATE_URL)

    def assert_retrieve_team_related_view(
            self,
            url_name: str,
            must_pass: bool = True,
            slug: str = None
    ) -> None:
        if not slug:
            slug = self.founded_team.slug
        assert_url_access(self, url_name, 200, must_pass, team_slug=slug)

    def test_retrieve_team_detail_page(self):
        self.assert_retrieve_team_related_view(TEAM_DETAIL_URL_NAME)

    def test_retrieve_team_update_page_for_founder(self):
        self.assert_retrieve_team_related_view(TEAM_UPDATE_URL_NAME)

    def test_discard_team_update_page_for_not_founder(self):
        self.assert_retrieve_team_related_view(
            TEAM_UPDATE_URL_NAME,
            must_pass=False,
            slug=self.involved_team.slug
        )

    def test_retrieve_team_delete_page_for_founder(self):
        self.assert_retrieve_team_related_view(TEAM_DELETE_URL_NAME)

    def test_discard_team_delete_page_for_not_founder(self):
        self.assert_retrieve_team_related_view(
            TEAM_DELETE_URL_NAME,
            must_pass=False,
            slug=self.involved_team.slug
        )

    def assert_team_kick_member_url_correct_access(
            self,
            team: Team,
            expected_status_code: int,
            member_must_be_kicked: bool = False
    ):
        several_person = get_user_model().objects.create(
            username="test.several.person"
        )
        team.members.add(several_person)
        team.save()
        assert_url_access(
            self,
            TEAM_KICK_MEMBER_URL_NAME,
            expected_status_code,
            team_slug=team.slug,
            member_username=several_person.username
        )
        if member_must_be_kicked:
            self.assertNotIn(several_person, team.members.all())

    def test_retrieve_team_kick_member_url_for_founder(self):
        self.assert_team_kick_member_url_correct_access(
            self.founded_team, 302, True
        )

    def test_discard_team_kick_member_url_for_not_founder(self):
        self.assert_team_kick_member_url_correct_access(
            self.involved_team, 403
        )


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


class PrivateProjectTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.user",
            password="test_password"
        )
        self.founded_team = Team.objects.create(
            name="Test founded team",
            founder=self.user
        )
        self.involved_team = Team.objects.create(
            name="Test involved team",
            founder=get_user_model().objects.create(username="test.big.boss")
        )
        self.involved_team.members.add(self.user)
        self.involved_team.save()
        self.founded_project = Project.objects.create(
            name="Founded project",
            working_team=self.founded_team
        )
        self.involved_project = Project.objects.create(
            name="Involved project",
            working_team=self.involved_team
        )
        self.client.force_login(self.user)

    def test_retrieve_project_create_page_for_founder(self):
        assert_url_access(
            self,
            PROJECT_CREATE_URL_NAME,
            team_slug=self.founded_team.slug
        )

    def test_discard_project_create_page_for_not_founder(self):
        assert_url_access(
            self,
            PROJECT_CREATE_URL_NAME,
            200,
            False,
            team_slug=self.involved_team.slug
        )

    def test_retrieve_project_detail_page(self):
        assert_url_access(
            self,
            PROJECT_DETAIL_URL_NAME,
            team_slug=self.founded_team.slug,
            project_slug=self.founded_project.slug
        )

    def test_retrieve_project_member_tasks_page_template_used(self):
        response = assert_url_access(
            self,
            PROJECT_MEMBER_TASKS_URL_NAME,
            team_slug=self.involved_team.slug,
            project_slug=self.involved_project.slug,
            user_slug=self.user.username
        )
        self.assertTemplateUsed(
            response,
            "task_manager/project_member_tasks.html"
        )

    def test_discard_project_member_tasks_page_for_not_member(self):
        assert_url_access(
            self,
            PROJECT_MEMBER_TASKS_URL_NAME,
            404,
            team_slug=self.founded_team.slug,
            project_slug=self.founded_project.slug,
            user_slug=self.user.username
        )
