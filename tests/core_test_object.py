"""Provides capabilities for mocking Thermoworks Cloud related API calls."""

from typing import cast
from pytest_httpserver import HTTPServer, RequestHandler

from tests.test_data import (
    API_KEY,
    FIREBASE_APPLICATION_BASE_PATH,
    TEST_USER_ID,
)
from thermoworks_cloud.auth import _Auth, Auth


class CoreTestObject:
    """A test object that can be used to mock Thermoworks Cloud related API calls."""

    def __init__(self, httpserver: HTTPServer, auth: Auth) -> None:
        """Create a new test object for the Core module

        Args:
            httpserver (HTTPServer): The http server to use when mocking requests
            auth (Auth): The Auth object to use with this test object
        """
        self.httpserver = httpserver
        self.auth = cast(_Auth, auth)

    def expect_get_user(self, access_token: str) -> RequestHandler:
        """Create a request handler for a GET request to the `get_user` API."""
        url = f"{FIREBASE_APPLICATION_BASE_PATH}/users/{TEST_USER_ID}"
        headers = {"authorization": f"Bearer {access_token}"}
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(
            url, headers=headers, query_string=query_string
        )

    def expect_get_device(
        self, access_token: str, device_serial: str
    ) -> RequestHandler:
        """Create a request handler for a GET request to the `get_device` API."""
        url = f"{FIREBASE_APPLICATION_BASE_PATH}/devices/{device_serial}"
        headers = {"authorization": f"Bearer {access_token}"}
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(
            url, headers=headers, query_string=query_string
        )

    def expect_get_device_channel(
        self, access_token: str, device_serial: str, channel: str
    ) -> RequestHandler:
        """Create a request handler for a GET request to the `get_device_channel` API.
        """
        url = f"{
            FIREBASE_APPLICATION_BASE_PATH}/devices/{device_serial}/channels/{channel}"
        headers = {"authorization": f"Bearer {access_token}"}
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(
            url, headers=headers, query_string=query_string
        )
