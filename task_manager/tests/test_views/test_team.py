from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .utils import assert_url_access
from task_manager.models import Team

TEAM_LIST_URL = reverse("task_manager:team-list")
TEAM_CREATE_URL = reverse("task_manager:team-create")
TEAM_DETAIL_URL_NAME = "task_manager:team-detail"
TEAM_UPDATE_URL_NAME = "task_manager:team-update"
TEAM_DELETE_URL_NAME = "task_manager:team-delete"
TEAM_KICK_MEMBER_URL_NAME = "task_manager:team-kick-member"


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


class UserTeamTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.user",
            password="user_password"
        )
        self.team = Team.objects.create(
            name="Test involved team",
            founder=get_user_model().objects.create(username="test.big.boss")
        )
        self.client.force_login(self.user)

    def test_retrieve_team_create_page(self):
        assert_url_access(self, TEAM_CREATE_URL)


class MemberTeamTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.member",
            password="member_password"
        )
        self.involved_team = Team.objects.create(
            name="Test involved team",
            founder=get_user_model().objects.create(username="test.big.boss")
        )
        self.another_member = get_user_model().objects.create(
            username="another.member"
        )
        self.involved_team.members.add(self.user, self.another_member)
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

    def test_retrieve_team_detail_page_for_member(self):
        assert_url_access(
            self,
            TEAM_DETAIL_URL_NAME,
            team_slug=self.involved_team.slug
        )

    def test_discard_team_update_page_for_not_founder(self):
        assert_url_access(
            self,
            TEAM_UPDATE_URL_NAME,
            403,
            team_slug=self.involved_team.slug
        )

    def test_discard_team_delete_page_for_not_founder(self):
        assert_url_access(
            self,
            TEAM_DELETE_URL_NAME,
            403,
            team_slug=self.involved_team.slug
        )

    def test_discard_team_kick_member_url_for_not_founder(self):
        assert_url_access(
            self,
            TEAM_KICK_MEMBER_URL_NAME,
            403,
            team_slug=self.involved_team.slug,
            member_username=self.another_member.username
        )


class FounderTeamTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.founder",
            password="founder_password"
        )
        self.founded_team = Team.objects.create(
            name="Test founded team",
            founder=self.user
        )
        self.member = get_user_model().objects.create(username="member")
        self.founded_team.members.add(self.member)
        self.client.force_login(self.user)

    def test_retrieve_team_detail_page_for_founder(self):
        assert_url_access(
            self,
            TEAM_DETAIL_URL_NAME,
            team_slug=self.founded_team.slug
        )

    def test_retrieve_team_update_page_for_founder(self):
        assert_url_access(
            self,
            TEAM_UPDATE_URL_NAME,
            team_slug=self.founded_team.slug
        )

    def test_retrieve_team_delete_page_for_founder(self):
        assert_url_access(
            self,
            TEAM_DELETE_URL_NAME,
            team_slug=self.founded_team.slug
        )

    def test_retrieve_team_kick_member_url_for_founder(self):
        assert_url_access(
            self,
            TEAM_KICK_MEMBER_URL_NAME,
            302,
            True,
            team_slug=self.founded_team.slug,
            member_username=self.member.username
        )
