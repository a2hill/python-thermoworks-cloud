"""Provides capabilities for mocking ThermoWorks API calls."""

from typing import Optional

from pytest_httpserver import HTTPServer, RequestHandler


class ClientTestObject:
    """A test object that can be used to mock ThermoWorks API calls."""

    def __init__(self, httpserver: HTTPServer) -> None:
        """Create a new test object for the Client module

        Args:
            httpserver (HTTPServer): The http server to use when mocking requests
        """
        self.httpserver = httpserver
        self.base_url = httpserver.url_for("/api")

    def expect_get_me(self, api_key: str) -> RequestHandler:
        """Create a request handler for a GET request to the `/v1/me` API."""
        headers = {"authorization": f"Bearer {api_key}"}
        return self.httpserver.expect_ordered_request(
            "/api/v1/me", method="GET", headers=headers
        )

    def expect_get_devices(self, api_key: str, etag: Optional[str] = None) -> RequestHandler:
        """Create a request handler for a GET request to the `/v1/devices` API."""
        headers = {"authorization": f"Bearer {api_key}"}
        if etag is not None:
            headers["If-None-Match"] = etag
        return self.httpserver.expect_ordered_request(
            "/api/v1/devices", method="GET", headers=headers
        )
