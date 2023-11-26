from django.urls import path

from task_manager.views import HomePageView, TeamListView

urlpatterns = [
    path("", HomePageView.as_view(), name="index"),
    path("teams/", TeamListView.as_view(), name="team-list")
]

app_name = "task_manager"
