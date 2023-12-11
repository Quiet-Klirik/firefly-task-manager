from abc import abstractmethod

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views import generic

from task_manager.forms import UserRegistrationForm, TeamForm, ProjectForm, \
    TaskForm, TaskForOneAssigneeForm
from task_manager.models import Team, Project, Worker, Task


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
        response = super().dispatch(request, *args, **kwargs)
        if request.user != self.get_founder():
            return self.handle_no_permission()
        return response


class MemberOrFounderLoginRequiredMixin(LoginRequiredMixin):
    @abstractmethod
    def get_team(self) -> Team:
        pass

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if (
                request.user not in self.get_team().members.all()
                and request.user != self.get_team().founder
        ):
            return self.handle_no_permission()
        return response


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


class ProjectDetailView(generic.DetailView):
    model = Project
    queryset = Project.objects.select_related(
        "working_team__founder"
    ).prefetch_related("working_team__members")

    def get_object(self, queryset=None):
        project_slug = self.kwargs.get("project_slug")
        return self.queryset.get(slug=project_slug)


class ProjectMembersView(MemberOrFounderLoginRequiredMixin, ProjectDetailView):
    queryset = Project.objects.select_related(
        "working_team__founder"
    ).prefetch_related("working_team__members")

    def get_team(self) -> Team:
        return self.get_object().working_team


class ProjectLandingView(ProjectDetailView):
    template_name = "task_manager/project_landing.html"


class ProjectMemberTasksView(
    MemberOrFounderLoginRequiredMixin,
    generic.DetailView
):
    model = get_user_model()
    slug_field = "username"
    slug_url_kwarg = "user_slug"
    template_name = "task_manager/project_member_tasks.html"
    project = None

    def get_project(self) -> Project:
        if not self.project:
            project_slug = self.kwargs.get("project_slug")
            project = Project.objects.select_related(
                "working_team__founder"
            ).prefetch_related("working_team__members").get(slug=project_slug)
            self.project = project
        return self.project

    def get_team(self) -> Team:
        return self.get_project().working_team

    def get_object(self, queryset=None):
        user_username = self.kwargs.get("user_slug")
        return get_object_or_404(
            self.get_project().working_team.members.select_related("position"),
            username=user_username
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.get_project()
        member = self.get_object()
        context["project"] = project
        context["requested_tasks"] = member.requested_tasks.filter(
            project=project
        )
        context["assigned_tasks"] = member.assigned_tasks.filter(
            project=project
        )
        return context


class ProjectUpdateView(FounderLoginRequiredMixin, generic.UpdateView):
    model = Project
    form_class = ProjectForm

    def get_object(self, queryset=None):
        project_slug = self.kwargs.get("project_slug")
        return get_object_or_404(
            self.model.objects.select_related("working_team__founder"),
            slug=project_slug
        )

    def get_founder(self):
        return self.get_object().working_team.founder

    def form_valid(self, form):
        form.instance.working_team = self.get_object().working_team
        return super().form_valid(form)


class ProjectDeleteView(FounderLoginRequiredMixin, generic.DeleteView):
    model = Project

    def get_object(self, queryset=None):
        project_slug = self.kwargs.get("project_slug")
        return get_object_or_404(
            self.model.objects.select_related("working_team__founder"),
            slug=project_slug
        )

    def get_founder(self):
        return self.get_object().working_team.founder

    def get_success_url(self):
        return reverse_lazy(
            "task_manager:team-detail",
            kwargs={"team_slug": self.get_object().working_team.slug}
        )


class TaskCreateView(MemberOrFounderLoginRequiredMixin, generic.CreateView):
    model = Task
    form_class = TaskForm
    project = None

    def get_project(self) -> Project:
        if not self.project:
            project_slug = self.kwargs.get("project_slug")
            project = Project.objects.select_related(
                "working_team__founder"
            ).prefetch_related("working_team__members").get(slug=project_slug)
            self.project = project
        return self.project

    def get_team(self) -> Team:
        return self.get_project().working_team

    def get_initial(self):
        initial = super().get_initial()
        initial["team_slug"] = self.kwargs.get("team_slug")
        return initial

    def form_valid(self, form):
        form.instance.project = self.get_project()
        form.instance.requester = self.request.user
        return super().form_valid(form)


class TaskAssignView(TaskCreateView):
    form_class = TaskForOneAssigneeForm

    def form_valid(self, form):
        response = super().form_valid(form)
        user_username = self.kwargs.get("user_slug")
        user = get_user_model().objects.get(username=user_username)
        form.instance.assignees.add(user)
        return response


class TaskDetailView(MemberOrFounderLoginRequiredMixin, generic.DetailView):
    model = Task

    def get_object(self, queryset=None):
        task_id = self.kwargs.get("task_id")
        return self.model.objects.select_related(
            "project__working_team__founder", "task_type", "requester"
        ).prefetch_related(
            "project__working_team__members", "assignees"
        ).get(id=task_id)

    def get_team(self) -> Team:
        return self.get_object().project.working_team
