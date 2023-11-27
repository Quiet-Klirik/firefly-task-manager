from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic

from task_manager.forms import UserRegistrationForm, TeamForm
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


class UserProfileDetailView(LoginRequiredMixin, generic.DetailView):
    model = get_user_model()
    queryset = get_user_model().objects.select_related("position")
    slug_field = "username"

    def get(self, request, *args, **kwargs):
        if "slug" not in kwargs:
            url = reverse_lazy(
                "profile",
                kwargs={"slug": request.user.username}
            )
            return redirect(url)
        return super().get(self, request, *args, **kwargs)


class UserProfileEditView(LoginRequiredMixin, generic.UpdateView):
    model = get_user_model()
    fields = (
        "username",
        "first_name",
        "last_name",
        "position",
    )
    slug_field = "username"

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        return reverse_lazy(
            "profile",
            kwargs={"slug": self.get_object().username}
        )


class UserDeleteView(LoginRequiredMixin, generic.DeleteView):
    model = get_user_model()
    slug_field = "username"
    success_url = reverse_lazy("task_manager:index")

    def get_object(self, queryset=None):
        return self.request.user


class TeamListView(LoginRequiredMixin, generic.TemplateView):
    model = Team
    template_name = "task_manager/team_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context["involved_teams"] = user.teams.all()
        context["founded_teams"] = user.founded_teams.all()
        return context


class TeamCreateView(LoginRequiredMixin, generic.CreateView):
    model = Team
    form_class = TeamForm

    def form_valid(self, form):
        form.instance.founder = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "task_manager:team-detail",
            kwargs={"slug": self.object.slug}
        )


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team

    def get_object(self, queryset=None):
        return self.model.objects.select_related(
            "founder"
        ).prefetch_related(
            "members", "projects"
        ).get(slug=self.kwargs.get("slug"))
