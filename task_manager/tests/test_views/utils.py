from unittest import TestCase

from django.urls import reverse


def assert_url_access(
        self: TestCase,
        url_name: str,
        status_code: int = 200,
        must_equals: bool = True,
        **kwargs
):
    """
    Checks that URL response is equal or not equal to the expected status code
    :returns: response object
    """
    if url_name.startswith("/"):
        url = url_name
    else:
        url = reverse(url_name, kwargs=kwargs)
    response = self.client.get(url)
    if must_equals:
        self.assertEquals(response.status_code, status_code)
    else:
        self.assertNotEquals(response.status_code, status_code)
    return response