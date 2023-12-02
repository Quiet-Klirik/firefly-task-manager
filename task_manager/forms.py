from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django.forms import ModelForm

from task_manager.models import Team, Project


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "first_name",
            "last_name",
            "position",
            "password1",
            "password2"
        )


class TeamForm(ModelForm):
    class Meta:
        model = Team
        fields = "__all__"
        widgets = {
            "members": forms.CheckboxSelectMultiple
        }

    founder = forms.ModelChoiceField(
        queryset=get_user_model().objects.all(),
        widget=forms.HiddenInput,
        required=False
    )


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = "__all__"

    working_team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        widget=forms.HiddenInput,
        required=False
    )
