"""Provides capabilities for mocking authentication related API calls."""

from pytest_httpserver import HTTPServer, RequestHandler

from tests.test_data import (
    API_KEY,
    FIREBASE_APPLICATION_BASE_PATH,
    LOGIN_PATH,
    TOKEN_PATH,
    WEB_CONFIG_PATH,
)


class AuthTestObject:
    """A test object that can be used to mock authentication related API calls."""

    def __init__(self, httpserver: HTTPServer) -> None:
        """Create a new AuthTestObject

        Args:
            httpserver (HTTPServer): The httpserver that the test object will use to mock responses
        """
        self.httpserver = httpserver

    def expect_config(self) -> RequestHandler:
        """Create a request handler for a `get web config` request."""
        headers = {"x-goog-api-key": API_KEY, "accept": "application/json"}
        return self.httpserver.expect_request(WEB_CONFIG_PATH, headers=headers)

    def expect_login(self, email: str, password: str) -> RequestHandler:
        """Create a request handler for a `sign in with email` request."""
        headers = {"Content-Type": "application/json"}
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(
            LOGIN_PATH,
            headers=headers,
            query_string=query_string,
            json={
                "email": email,
                "password": password,
                "returnSecureToken": True,
            },
        )

    def expect_token_refresh(self, refresh_token: str) -> RequestHandler:
        """Create a request handler for a `refresh token` request."""
        headers = {"Content-Type": "application/json"}
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(
            TOKEN_PATH,
            headers=headers,
            query_string=query_string,
            json={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
            },
        )

    def expect_request(self, path: str, headers: dict) -> RequestHandler:
        """Create a request handler for a generic request to this firestore project."""
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(
            f"{FIREBASE_APPLICATION_BASE_PATH}/{path}",
            headers=headers,
            query_string=query_string,
        )
