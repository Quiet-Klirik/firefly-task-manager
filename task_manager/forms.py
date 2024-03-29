from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from django.forms import ModelForm
from django_select2.forms import (
    ModelSelect2TagWidget,
    ModelSelect2MultipleWidget
)
from taggit.models import Tag

from task_manager.models import Team, Project, Task, TaskType


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "position",
            "password1",
            "password2",
        )


class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = "__all__"

    founder = forms.ModelChoiceField(
        queryset=None, widget=forms.HiddenInput, required=False
    )
    members = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.select_related("position"),
        widget=ModelSelect2MultipleWidget(
            model=get_user_model(),
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "position__name__icontains"
            ],
            attrs={
                "data-placeholder": "Choose members"
            },
        )
    )


class TeamUpdateForm(TeamForm):
    def __init__(self, *args, **kwargs):
        members_queryset = kwargs["initial"].pop("members_queryset", None)
        super().__init__(*args, **kwargs)
        self.fields["founder"].queryset = members_queryset

    founder = forms.ModelChoiceField(
        queryset=None,
        required=False,
    )


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

    working_team = forms.ModelChoiceField(
        queryset=Team.objects.all(), widget=forms.HiddenInput, required=False
    )


class ModelMultipleAutocompleteChoiceWidget(ModelSelect2TagWidget):
    """
    Implements user-friendly ModelMultipleChoiceField design
    with autocomplete and auto-creating a non-existing objects
    """

    create_field = "name"
    many = True

    def __init__(self, *args, **kwargs):
        self.create_field = kwargs.pop("create_field", self.create_field)
        self.many = kwargs.pop("many", self.many)
        super().__init__(*args, **kwargs)

    def value_from_datadict(self, data, files, name):
        values = super().value_from_datadict(data, files, name)
        cleaned_values = [
            value
            if value.isdigit()
            and self.model.objects.filter(pk=int(value)).exists()
            else str(self.model.objects.get_or_create(
                **{self.create_field: value}
            )[0].pk)
            for value in values
        ]
        if not self.many and cleaned_values:
            return self.model.objects.get(pk=cleaned_values[0])
        return cleaned_values

    def value_omitted_from_data(self, data, files, name):
        return False


class TaskForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        team_slug = kwargs["initial"].pop('team_slug', None)
        super().__init__(*args, **kwargs)
        assignees_queryset = self.fields['assignees'].queryset
        if team_slug and assignees_queryset:
            self.fields['assignees'].queryset = assignees_queryset.filter(
                teams__slug=team_slug
            )

    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=ModelMultipleAutocompleteChoiceWidget(
            model=Tag,
            search_fields=["name__icontains"],
            attrs={
                "data-placeholder": "None",
            },
        ),
    )
    task_type = forms.ModelChoiceField(
        queryset=TaskType.objects.all(),
        widget=ModelMultipleAutocompleteChoiceWidget(
            model=TaskType,
            many=False,
            search_fields=["name__icontains"],
            attrs={
                "data-maximum-selection-length": 1,
                "data-placeholder": "None"
            },
        ),
    )
    project = forms.ModelChoiceField(
        queryset=Project.objects, widget=forms.HiddenInput, required=False
    )
    requester = forms.ModelChoiceField(
        queryset=get_user_model().objects,
        widget=forms.HiddenInput,
        required=False
    )
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects.select_related("position"),
        widget=ModelSelect2MultipleWidget(
            model=get_user_model(),
            search_fields=[
                "first_name__icontains",
                "last_name__icontains",
                "position__name__icontains"
            ],
            attrs={
                "data-placeholder": "Choose assignees"
            },
        )
    )

    class Meta:
        model = Task
        fields = (
            "name",
            "tags",
            "description",
            "deadline",
            "priority",
            "task_type",
            "assignees",
            "project",
            "requester",
        )
        widgets = {
            "deadline": forms.DateInput(attrs={'type': 'date'}),
        }


class TaskForOneAssigneeForm(TaskForm):
    assignees = forms.ModelMultipleChoiceField(
        queryset=get_user_model().objects,
        widget=forms.HiddenInput,
        required=False
    )


class NotificationFilterByTeamForm(forms.Form):
    def __init__(self, *args, **kwargs):
        user_id = kwargs["initial"].pop("user_id", None)
        super().__init__(*args, **kwargs)
        if user_id:
            team_queryset = self.fields["team"].queryset
            self.fields["team"].queryset = team_queryset.filter(
                Q(founder_id=user_id) | Q(members__id=user_id),
            ).distinct()

    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        required=False,
    )


class NotificationFilterByProjectForm(forms.Form):
    def __init__(self, *args, **kwargs):
        team_id = kwargs["initial"].pop("team_id", None)
        super().__init__(*args, **kwargs)
        if team_id:
            project_queryset = self.fields["project"].queryset
            self.fields["project"].queryset = project_queryset.filter(
                working_team__id=team_id,
            )

    project = forms.ModelChoiceField(
        queryset=Project.objects.select_related("working_team"),
        required=False,
    )
