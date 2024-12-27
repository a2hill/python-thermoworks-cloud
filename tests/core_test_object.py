from typing import cast
from pytest_httpserver import HTTPServer, RequestHandler

from tests.test_data import API_KEY, TEST_PROJECT_ID, TEST_USER_ID
from thermoworks_cloud.auth import _Auth, Auth

class CoreTestObject:
    
    def __init__(self, httpserver: HTTPServer, auth: Auth) -> None:
        self.httpserver = httpserver
        self.auth = cast(_Auth, auth)
    
    def expect_get_user(self, access_token: str) -> RequestHandler:
        url = f"/v1/projects/{TEST_PROJECT_ID}/databases/(default)/documents/users/{TEST_USER_ID}"
        headers = {
            "authorization": f"Bearer {access_token}"
        }
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(url, headers=headers, query_string=query_string)
    
    def expect_get_device(self, access_token: str, device_serial: str) -> RequestHandler:
        url = f"/v1/projects/{TEST_PROJECT_ID}/databases/(default)/documents/devices/{device_serial}"
        headers = {
            "authorization": f"Bearer {access_token}"
        }
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(url, headers=headers, query_string=query_string)
    
    def expect_get_device_channel(self, access_token: str, device_serial: str, channel: str) -> RequestHandler:
        url = f"/v1/projects/{TEST_PROJECT_ID}/databases/(default)/documents/devices/{device_serial}/channels/{channel}"
        headers = {
            "authorization": f"Bearer {access_token}"
        }
        query_string = {"key": API_KEY}
        return self.httpserver.expect_request(url, headers=headers, query_string=query_string)
