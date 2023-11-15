from django.urls import path

from task_manager.views import HomePageView

urlpatterns = [
    path("", HomePageView.as_view(), name="index")
]

app_name = "task_manager"
