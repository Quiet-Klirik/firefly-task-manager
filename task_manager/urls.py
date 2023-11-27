from django.urls import path

from task_manager.views import HomePageView, TeamListView, TeamCreateView, \
    TeamDetailView, TeamUpdateView

urlpatterns = [
    path("", HomePageView.as_view(), name="index"),
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("teams/create/", TeamCreateView.as_view(), name="team-create"),
    path("<str:slug>/", TeamDetailView.as_view(), name="team-detail"),
    path("<str:slug>/edit/", TeamUpdateView.as_view(), name="team-update")
]

app_name = "task_manager"
