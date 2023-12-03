from django.urls import path

from task_manager.views import (
    HomePageView,
    TeamListView,
    TeamCreateView,
    TeamDetailView,
    TeamUpdateView,
    TeamDeleteView,
    TeamKickMemberView,
    ProjectCreateView,
    ProjectMembersView,
    ProjectLandingView,
    ProjectMemberTasksView, ProjectUpdateView, ProjectDeleteView
)

urlpatterns = [
    path("", HomePageView.as_view(), name="index"),
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("teams/create/", TeamCreateView.as_view(), name="team-create"),
    path(
        "<str:team_slug>/",
        TeamDetailView.as_view(),
        name="team-detail"
    ),
    path(
        "<str:team_slug>/edit/",
        TeamUpdateView.as_view(),
        name="team-update"
    ),
    path(
        "<str:team_slug>/delete/",
        TeamDeleteView.as_view(),
        name="team-delete"
    ),
    path(
        "<str:team_slug>/kick/<str:member_username>/",
        TeamKickMemberView.as_view(),
        name="team-kick-member"
    ),
    path(
        "<str:team_slug>/create-project/",
        ProjectCreateView.as_view(),
        name="project-create"
    ),
    path(
        "<str:team_slug>/<str:project_slug>/",
        ProjectMembersView.as_view(),
        name="project-detail"
    ),
    path(
        "<str:team_slug>/<str:project_slug>/landing/",
        ProjectLandingView.as_view(),
        name="project-landing"
    ),
    path(
        "<str:team_slug>/<str:project_slug>/edit/",
        ProjectUpdateView.as_view(),
        name="project-update"
    ),
    path(
        "<str:team_slug>/<str:project_slug>/delete/",
        ProjectDeleteView.as_view(),
        name="project-delete"
    ),
    path(
        "<str:team_slug>/<str:project_slug>/<str:user_slug>/",
        ProjectMemberTasksView.as_view(),
        name="project-member-tasks"
    )
]

app_name = "task_manager"
