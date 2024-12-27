"""
Configures pytest for all tests, providing various fixtures
"""
from unittest.mock import patch
from aiohttp import ClientSession
import pytest
from pytest_httpserver import HTTPServer

from tests.core_test_object import CoreTestObject
from tests.test_data import CONFIG_RETURN_VALUE
from tests.test_data import LOGIN_RETURN_VALUE, TEST_EMAIL_ADDRESS, TEST_PASSWORD
from thermoworks_cloud.auth import _TokenManager, Auth, AuthFactory
from tests.auth_test_object import AuthTestObject


@pytest.fixture(autouse=True)
def httpserver_endpoint(httpserver: HTTPServer) -> str:
    return f"http://{httpserver.host}:{httpserver.port}"

@pytest.fixture(autouse=True)
def override_token_manager_hosts(httpserver_endpoint: str):
    """Override the hosts that _TokenManager uses so that it will call our mock http server"""

    with patch.object(_TokenManager, '_IDENTITY_HOST', httpserver_endpoint):
        with patch.object(_TokenManager, '_TOKEN_HOST', httpserver_endpoint):
            yield

@pytest.fixture(autouse=True)
def override_authfactory_hosts(httpserver_endpoint: str):
    """Override the hosts that AuthFactory uses so that it will call our mock http server"""

    with patch.object(AuthFactory, '_FIREBASE_HOST', httpserver_endpoint):
        with patch.object(AuthFactory, '_FIRESTORE_HOST', httpserver_endpoint):
            yield

@pytest.fixture()
def auth_test_object(httpserver: HTTPServer) -> AuthTestObject:
    return AuthTestObject(httpserver)

@pytest.fixture()
async def client_session():
    client_session = ClientSession()
    yield client_session

    # Runs after the test completes
    await client_session.close()

@pytest.fixture()
async def auth(client_session: ClientSession, auth_test_object: AuthTestObject) -> Auth:
    """
    Provides an Auth object for use in component tests. 
    """
    # Setup mock responses
    auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
    auth_test_object.expect_login(
        TEST_EMAIL_ADDRESS, TEST_PASSWORD).respond_with_json(LOGIN_RETURN_VALUE)
    # Build and return Auth
    return await AuthFactory(client_session).build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)

@pytest.fixture()
def core_test_object(httpserver: HTTPServer, auth: Auth) -> CoreTestObject:
    return CoreTestObject(httpserver, auth)