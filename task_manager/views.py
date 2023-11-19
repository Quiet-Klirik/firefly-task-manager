from django.contrib.auth import get_user_model
from django.urls import reverse_lazy
from django.views import generic

from task_manager.forms import UserRegistrationForm
from task_manager.models import Team, Project, Worker


class HomePageView(generic.TemplateView):
    template_name = "task_manager/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["teams_count"] = Team.objects.count()
        context["projects_count"] = Project.objects.count()
        context["workers_count"] = Worker.objects.count()
        return context


class UserRegisterView(generic.CreateView):
    model = get_user_model()
    form_class = UserRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("task_manager:index")
