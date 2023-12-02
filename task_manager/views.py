from abc import abstractmethod

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from task_manager.forms import UserRegistrationForm, TeamForm, ProjectForm
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


class TeamDetailView(LoginRequiredMixin, generic.DetailView):
    model = Team
    slug_url_kwarg = "team_slug"

    def get_object(self, queryset=None):
        return self.model.objects.select_related(
            "founder"
        ).prefetch_related(
            "members", "projects"
        ).get(slug=self.kwargs.get("team_slug"))


class FounderLoginRequiredMixin(LoginRequiredMixin):
    permission_denied_message = "Access denied"

    @abstractmethod
    def get_founder(self):
        pass

    def dispatch(self, request, *args, **kwargs):
        if request.user != self.get_founder():
            return self.handle_no_permission()
        return super().dispatch(request, *args, **kwargs)


class TeamUpdateView(FounderLoginRequiredMixin, generic.UpdateView):
    model = Team
    form_class = TeamForm
    slug_url_kwarg = "team_slug"

    def get_founder(self):
        return self.get_object().founder


class TeamDeleteView(FounderLoginRequiredMixin, generic.DeleteView):
    model = Team
    slug_url_kwarg = "team_slug"
    success_url = reverse_lazy("task_manager:team-list")

    def get_founder(self):
        return self.get_object().founder


class TeamKickMemberView(FounderLoginRequiredMixin, generic.DetailView):
    model = Team
    slug_url_kwarg = "team_slug"

    def get_object(self, queryset=None):
        team_slug = self.kwargs.get(self.slug_url_kwarg)
        return get_object_or_404(
            self.model.objects.select_related("founder"),
            slug=team_slug
        )

    def get_member(self):
        member_username = self.kwargs.get("member_username")
        member = self.get_object().members.get(username=member_username)
        return member

    def get_founder(self):
        return self.get_object().founder

    def get_success_url(self):
        return reverse_lazy(
            "task_manager:team-detail",
            kwargs={"team_slug": self.get_object().slug}
        )

    def get(self, request, *args, **kwargs):
        self.get_object().members.remove(self.get_member())
        return redirect(self.get_success_url())


class ProjectCreateView(FounderLoginRequiredMixin, generic.CreateView):
    model = Project
    form_class = ProjectForm
    team = None

    def get_team(self) -> Team:
        if not self.team:
            team_slug = self.kwargs.get("team_slug")
            team = get_object_or_404(
                Team.objects.select_related("founder"),
                slug=team_slug
            )
            self.team = team
        return self.team

    def get_founder(self):
        return self.get_team().founder

    def form_valid(self, form):
        form.instance.working_team = self.get_team()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            "task_manager:team-detail",
            kwargs={"team_slug": self.get_team().slug}
        )
