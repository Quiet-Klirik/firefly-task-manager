import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase

from task_manager.models import Team, Project, TaskType, Task
from .utils import assert_url_access

TASK_CREATE_URL_NAME = "task_manager:task-create"
TASK_ASSIGN_URL_NAME = "task_manager:project-member-assign-task"
TASK_DETAIL_URL_NAME = "task_manager:task-detail"
TASK_UPDATE_URL_NAME = "task_manager:task-update"
TASK_DELETE_URL_NAME = "task_manager:task-delete"


class PublicTaskTests(TestCase):
    def setUp(self) -> None:
        self.team = Team.objects.create(
            name="Test founded team",
        )
        self.member = get_user_model().objects.create(username="member")
        self.team.members.add(self.member)
        self.project = Project.objects.create(
            name="Test founded project",
            working_team=self.team
        )
        self.task_type = TaskType.objects.create(name="Test task type")
        self.task = Task.objects.create(
            name="Test task",
            project=self.project,
            deadline=datetime.date(2222, 2, 22),
            task_type=self.task_type,
        )

    def test_task_create_login_required(self):
        assert_url_access(
            self,
            TASK_CREATE_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_task_assign_login_required(self):
        assert_url_access(
            self,
            TASK_ASSIGN_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            user_slug=self.member.username,
        )

    def test_task_detail_login_required(self):
        assert_url_access(
            self,
            TASK_DETAIL_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_task_update_login_required(self):
        assert_url_access(
            self,
            TASK_UPDATE_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_task_delete_login_required(self):
        assert_url_access(
            self,
            TASK_DELETE_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )


class TeamFounderTaskTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="team.founder"
        )
        self.team = Team.objects.create(
            name="Founded team",
            founder=self.user
        )
        self.member = get_user_model().objects.create(username="member")
        self.team.members.add(self.member)
        self.project = Project.objects.create(
            name="Founded project",
            working_team=self.team
        )
        self.task_type = TaskType.objects.create(name="Test task type")
        self.task = Task.objects.create(
            name="Test task",
            project=self.project,
            deadline=datetime.date(2222, 2, 22),
            task_type=self.task_type,
            requester=self.member
        )
        self.client.force_login(self.user)

    def test_retrieve_task_create_page_for_founder(self):
        assert_url_access(
            self,
            TASK_CREATE_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_retrieve_task_assign_page_for_founder(self):
        assert_url_access(
            self,
            TASK_ASSIGN_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            user_slug=self.member.username,
        )

    def test_retrieve_task_detail_page_for_founder(self):
        assert_url_access(
            self,
            TASK_DETAIL_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )


class MemberTaskTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="team.member"
        )
        self.team = Team.objects.create(
            name="Involved team"
        )
        self.member = get_user_model().objects.create(username="member")
        self.team.members.add(self.user, self.member)
        self.project = Project.objects.create(
            name="Involved project",
            working_team=self.team
        )
        self.task_type = TaskType.objects.create(name="Test task type")
        self.task = Task.objects.create(
            name="Test task",
            project=self.project,
            deadline=datetime.date(2222, 2, 22),
            task_type=self.task_type,
            requester=self.user
        )
        self.client.force_login(self.user)

    def test_retrieve_task_create_page_for_member(self):
        assert_url_access(
            self,
            TASK_CREATE_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_retrieve_task_assign_page_for_member(self):
        assert_url_access(
            self,
            TASK_ASSIGN_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            user_slug=self.member.username,
        )

    def test_retrieve_task_detail_page_for_member(self):
        assert_url_access(
            self,
            TASK_DETAIL_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_retrieve_task_update_page_for_requester(self):
        assert_url_access(
            self,
            TASK_UPDATE_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_retrieve_task_delete_page_for_requester(self):
        assert_url_access(
            self,
            TASK_DELETE_URL_NAME,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_discard_task_update_page_for_not_requester(self):
        self.client.logout()
        self.client.force_login(self.member)
        assert_url_access(
            self,
            TASK_UPDATE_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )

    def test_discard_task_delete_page_for_not_requester(self):
        self.client.logout()
        self.client.force_login(self.member)
        assert_url_access(
            self,
            TASK_DELETE_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )


class NotInvolvedUserTaskTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="not.involved.user"
        )
        self.team = Team.objects.create(
            name="Test team"
        )
        self.member = get_user_model().objects.create(username="member")
        self.team.members.add(self.member)
        self.project = Project.objects.create(
            name="Test project",
            working_team=self.team
        )
        self.task_type = TaskType.objects.create(name="Test task type")
        self.task = Task.objects.create(
            name="Test task",
            project=self.project,
            deadline=datetime.date(2222, 2, 22),
            task_type=self.task_type,
            requester=self.member
        )
        self.client.force_login(self.user)

    def test_retrieve_task_create_page_for_not_involved_user(self):
        assert_url_access(
            self,
            TASK_CREATE_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug
        )

    def test_retrieve_task_assign_page_for_not_involved_user(self):
        assert_url_access(
            self,
            TASK_ASSIGN_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            user_slug=self.member.username,
        )

    def test_retrieve_task_detail_page_for_not_involved_user(self):
        assert_url_access(
            self,
            TASK_DETAIL_URL_NAME,
            200,
            False,
            team_slug=self.team.slug,
            project_slug=self.project.slug,
            task_id=self.task.id
        )
