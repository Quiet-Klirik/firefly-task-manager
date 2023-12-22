from abc import abstractmethod

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from task_manager.models import Project


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
    def get_team(self):
        pass

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if (
                request.user not in self.get_team().members.all()
                and request.user != self.get_team().founder
        ):
            return self.handle_no_permission()
        return response


class TaskRequesterLoginRequiredMixin(LoginRequiredMixin):
    permission_denied_message = "Access denied"

    @abstractmethod
    def get_requester(self):
        pass

    def dispatch(self, request, *args, **kwargs):
        response = super().dispatch(request, *args, **kwargs)
        if request.method == "GET" and request.user != self.get_requester():
            return self.handle_no_permission()
        return response


class NotificationContextMixin:
    def get_notifications(self):
        return self.request.user.notifications.select_related(
            "notification_type",
            "task__project__working_team",
            "task__requester"
        ).filter(is_read=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            notifications = self.get_notifications().all()
            context["notifications"] = notifications
        return context


class TeamGetObjectMixin:
    object = None

    def get_object(self, queryset=None):
        if not self.object:
            self.object = self.model.objects.select_related(
                "founder"
            ).prefetch_related(
                "members", "projects"
            ).get(slug=self.kwargs.get("team_slug"))
        return self.object


class ViewGetProjectMixin:
    project = None

    def get_project(self) -> Project:
        if not self.project:
            project_slug = self.kwargs.get("project_slug")
            project = Project.objects.select_related(
                "working_team__founder"
            ).prefetch_related("working_team__members").get(slug=project_slug)
            self.project = project
        return self.project


class ProjectGetObjectMixin:
    object = None

    def get_object(self, queryset=None):
        if not self.object:
            project_slug = self.kwargs.get("project_slug")
            self.object = get_object_or_404(
                self.model.objects.select_related("working_team__founder"),
                slug=project_slug
            )
        return self.object


class TaskGetObjectMixin:
    object = None

    def get_object(self, queryset=None):
        if not self.object:
            task_id = self.kwargs.get("task_id")
            self.object = self.model.objects.select_related(
                "requester"
            ).get(id=task_id)
        return self.object
