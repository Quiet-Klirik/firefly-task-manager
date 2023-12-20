from abc import abstractmethod

from django.contrib.auth.mixins import LoginRequiredMixin


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
            "task__project__working_team",
            "task__requester"
        ).filter(is_read=False)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_authenticated:
            notifications = self.get_notifications().all()
            context["notifications"] = notifications
        return context
