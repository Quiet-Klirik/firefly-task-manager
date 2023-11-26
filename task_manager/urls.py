from django.urls import path

from task_manager.views import HomePageView, TeamListView, TeamCreateView

urlpatterns = [
    path("", HomePageView.as_view(), name="index"),
    path("teams/", TeamListView.as_view(), name="team-list"),
    path("teams/create", TeamCreateView.as_view(), name="team-create")
]

app_name = "task_manager"
