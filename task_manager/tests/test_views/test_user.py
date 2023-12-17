from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .utils import assert_url_access

USER_REGISTER_URL = reverse("register")
USER_PROFILE_URL_NAME = "profile"
USER_PROFILE_REDIRECT_URL = reverse("profile-redirect")
USER_PROFILE_EDIT_URL = reverse("profile-edit")
USER_PROFILE_DELETE_URL = reverse("profile-delete")


class PublicUserTests(TestCase):
    def test_user_register_using_template(self):
        response = assert_url_access(self, USER_REGISTER_URL)
        self.assertTemplateUsed(response, "registration/register.html")

    def assert_user_related_view_login_required(self, url_name: str) -> None:
        user = get_user_model().objects.create(username="test.user")
        assert_url_access(
            self,
            url_name,
            must_equals=False,
            slug=user.username
        )

    def test_user_profile_login_required(self):
        self.assert_user_related_view_login_required(USER_PROFILE_URL_NAME)

    def test_user_profile_redirect_login_required(self):
        assert_url_access(self, USER_PROFILE_REDIRECT_URL, 200, False)

    def test_user_profile_edit_login_required(self):
        assert_url_access(self, USER_PROFILE_EDIT_URL, 200, False)

    def test_user_profile_delete_login_required(self):
        assert_url_access(self, USER_PROFILE_DELETE_URL, 200, False)


class PrivateUserTests(TestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            username="test.user",
            password="test_password"
        )
        self.client.force_login(self.user)

    def assert_retrieve_user_related_view(self, url_name: str) -> None:
        assert_url_access(self, url_name, slug=self.user.username)

    def test_retrieve_user_profile_page(self):
        self.assert_retrieve_user_related_view(USER_PROFILE_URL_NAME)

    def test_redirect_user_profile_redirect_url(self):
        response = self.client.get(USER_PROFILE_REDIRECT_URL)
        expected_url = reverse(
            USER_PROFILE_URL_NAME,
            kwargs={"slug": self.user.username}
        )
        self.assertRedirects(response, expected_url)

    def test_retrieve_user_profile_edit_page(self):
        assert_url_access(self, USER_PROFILE_EDIT_URL)

    def test_user_profile_edit_object_is_current_user(self):
        response = assert_url_access(self, USER_PROFILE_EDIT_URL)
        context = response.context
        self.assertIn("object", context)
        self.assertEquals(context["object"], self.user)

    def test_retrieve_user_profile_delete(self):
        response = assert_url_access(self, USER_PROFILE_DELETE_URL)
        context_data = response.context
        self.assertIn("object", context_data)
        self.assertEquals(context_data["object"], self.user)
