from django.urls import path

from task_manager.views import HomePageView, TeamListView, TeamCreateView, \
    TeamDetailView, TeamUpdateView, TeamDeleteView

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
    )
]

app_name = "task_manager"
