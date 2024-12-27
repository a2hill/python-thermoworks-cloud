from pytest_httpserver import HTTPServer, RequestHandler

from tests.test_data import API_KEY, LOGIN_PATH, TEST_PROJECT_ID, TOKEN_PATH, WEB_CONFIG_PATH

class AuthTestObject:

    def __init__(self, httpserver: HTTPServer) -> None:
        self.httpserver = httpserver

    def expect_config(self) -> RequestHandler:
        headers = {
            "x-goog-api-key": API_KEY,
            "accept": "application/json"
        }
        return self.httpserver.expect_request(WEB_CONFIG_PATH, headers=headers)
    
    def expect_login(self, email: str, password: str) -> RequestHandler:
        headers = {
            "Content-Type": "application/json"
        }
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(LOGIN_PATH, headers=headers, query_string=query_string, json={
            "email": email,
            "password": password,
            "returnSecureToken": True,
        })
    
    def expect_token_refresh(self, refresh_token: str) -> RequestHandler:
        headers = {
            "Content-Type": "application/json"
        }
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(TOKEN_PATH, headers=headers, query_string=query_string, json={
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
        })
    
    def expect_request(self, path: str, headers: dict) -> RequestHandler:
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(f"/v1/projects/{TEST_PROJECT_ID}/databases/(default)/documents/{path}", headers=headers, query_string=query_string)