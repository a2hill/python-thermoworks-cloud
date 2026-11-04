"""HTTP expectations for the API client, following CoreTestObject's pattern."""

from datetime import datetime, timedelta, timezone
from email.utils import format_datetime
from unittest.mock import patch

from aiohttp import ClientSession
from pytest_httpserver import HTTPServer, RequestHandler

from thermoworks_cloud import ThermoworksClient
from tests.test_data import (
    API_TEST_KEY,
    API_DEVICE_RESPONSE,
    API_ME_RESPONSE,
    API_MISSING_DEVICES_RESPONSE,
    API_GATEWAY_RESPONSE,
    API_SIGNALS_RESPONSE,
)


class ApiTestObject:
    """Own API endpoints, bearer authentication, and mocked responses."""

    gateway_device_response = API_GATEWAY_RESPONSE
    signals_channel_response = API_SIGNALS_RESPONSE

    def __init__(self, httpserver: HTTPServer, session: ClientSession, key=API_TEST_KEY):
        """Configure the public client against the test server."""
        self.httpserver = httpserver
        self.key = key
        self.session = session
        self.client = ThermoworksClient(session, key, httpserver.url_for("/"))

    def expect_get_me(self) -> RequestHandler:
        """Expect account metadata with bearer authentication."""
        return self.httpserver.expect_oneshot_request(
            "/v1/me",
            method="GET",
            headers={"Authorization": f"Bearer {self.key}", "Accept": "application/json"},
        )

    def expect_get_device(self, access_token: str, device_serial: str) -> RequestHandler:
        """Adapt the shared device contract to the API's collection endpoint."""
        return self.expect_get_devices()

    def expect_get_device_channel(
        self, access_token: str, device_serial: str, channel: str
    ) -> RequestHandler:
        """Channel reads use the collection snapshot instead of Firestore paths."""
        return self.expect_get_devices()

    def expect_get_devices(self, etag: str | None = None) -> RequestHandler:
        """Expect a snapshot, optionally conditional on a previous ETag."""
        headers = {"Authorization": f"Bearer {self.key}", "Accept": "application/json"}
        if etag is not None:
            headers["If-None-Match"] = etag
        return self.httpserver.expect_oneshot_request("/v1/devices", method="GET", headers=headers)

    def respond_me(self):
        """Serve the account fixture."""
        self.expect_get_me().respond_with_json(API_ME_RESPONSE)

    def respond_devices(self):
        """Serve the device fixture with an ETag."""
        self.expect_get_devices().respond_with_json(
            API_DEVICE_RESPONSE, headers={"ETag": '"snapshot-1"'}
        )

    def respond_unchanged(self):
        """Serve a snapshot followed by a bodyless conditional response."""
        self.respond_devices()
        self.expect_get_devices('"snapshot-1"').respond_with_data(status=304)

    def respond_missing_devices(self):
        """Serve a malformed top-level response."""
        self.expect_get_devices().respond_with_json(API_MISSING_DEVICES_RESPONSE)

    def respond_invalid_device(self, device):
        """Serve a malformed device inside an otherwise valid envelope."""
        self.expect_get_devices().respond_with_json({"devices": [device]})

    def respond_rate_limited(self, retry_after="12"):
        """Reject a read with a retry delay."""
        self.expect_get_devices().respond_with_data(
            status=429, headers={"Retry-After": retry_after}
        )

    def respond_rate_limited_until_later(self):
        """Use the HTTP-date form of Retry-After."""
        self.respond_rate_limited(
            format_datetime(datetime.now(timezone.utc) + timedelta(seconds=60))
        )

    def respond_error(self, status):
        """Return an error body that must never appear in exceptions."""
        # Reflecting the request key simulates the worst case for error-body redaction.
        self.expect_get_devices().respond_with_data(self.key, status=status)

    def fail_transport(self, error_class):
        """Fail the caller-owned HTTP boundary, including a reflected credential."""
        return patch.object(self.session, "request", side_effect=error_class(self.key))
