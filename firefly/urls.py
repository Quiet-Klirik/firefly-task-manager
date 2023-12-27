"""
URL configuration for firefly project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.conf import settings
from django.urls import path, include
from django.views.decorators.cache import cache_page

from task_manager.views import (
    UserRegisterView,
    UserProfileDetailView, UserProfileEditView, UserDeleteView, IndexView
)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("-/", include("task_manager.urls", namespace="task_manager")),
    path("", cache_page(60**2 * 3)(IndexView.as_view()), name="index"),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/register/", UserRegisterView.as_view(), name="register"),
    path(
        "accounts/profile/",
        UserProfileDetailView.as_view(),
        name="profile-redirect"
    ),
    path(
        "accounts/<str:slug>/profile/",
        UserProfileDetailView.as_view(),
        name="profile"
    ),
    path(
        "accounts/profile/edit/",
        UserProfileEditView.as_view(),
        name="profile-edit"
    ),
    path(
        "accounts/profile/delete/",
        UserDeleteView.as_view(),
        name="profile-delete"
    ),
    path("select2/", include("django_select2.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path('__debug__/', include("debug_toolbar.urls")),
    ]
