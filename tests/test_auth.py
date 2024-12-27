from aiohttp import ClientSession, ClientResponseError

from tests.auth_test_object import AuthTestObject
from tests.test_data import CONFIG_RETURN_VALUE, LOGIN_RETURN_VALUE, TEST_EMAIL_ADDRESS, TEST_PASSWORD, TEST_USER_ID, TOKEN_REFRESH_RETURN_VALUE
from thermoworks_cloud.auth import AuthFactory, AuthenticationError, AuthenticationErrorReason
import pytest


class TestAuth:

    async def test_build_auth(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Test the happy path for building an auth object
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login(TEST_EMAIL_ADDRESS, TEST_PASSWORD).respond_with_json(LOGIN_RETURN_VALUE)

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        auth = await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        assert await auth.async_get_access_token() == LOGIN_RETURN_VALUE["idToken"]
        assert auth.user_id == TEST_USER_ID

    async def test_auth_refresh_token(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Test that the Auth object correctly refreshes the access token when it is close to exipry.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        # if the token expires in less than 60 seconds it should get refreshed when `async_get_access_token` is called
        auth_test_object.expect_login(TEST_EMAIL_ADDRESS, TEST_PASSWORD).respond_with_json(
            LOGIN_RETURN_VALUE | {"expiresIn": "10"})
        auth_test_object.expect_token_refresh(
            LOGIN_RETURN_VALUE["refreshToken"]).respond_with_json(TOKEN_REFRESH_RETURN_VALUE)

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        auth = await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        assert await auth.async_get_access_token() == TOKEN_REFRESH_RETURN_VALUE["access_token"]

        # shouldn't change the user id
        assert auth.user_id == TEST_USER_ID

    async def test_auth_refresh_token_refresh(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Each time the access token is refreshed, the next refresh call should use the refresh token from the previous call.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)

        # if the token expires in less than 60 seconds it should get refreshed when `async_get_access_token` is called
        auth_test_object.expect_login(TEST_EMAIL_ADDRESS, TEST_PASSWORD).respond_with_json(
            LOGIN_RETURN_VALUE | {"expiresIn": "10"})

        first_refresh_response = TOKEN_REFRESH_RETURN_VALUE | {
            "expires_in": "10"}
        second_refresh_response = TOKEN_REFRESH_RETURN_VALUE | {
            "access_token": "test-third-access-token"}
        auth_test_object.expect_token_refresh(
            LOGIN_RETURN_VALUE["refreshToken"]).respond_with_json(first_refresh_response)
        auth_test_object.expect_token_refresh(
            TOKEN_REFRESH_RETURN_VALUE["refresh_token"]).respond_with_json(second_refresh_response)

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        auth = await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        assert await auth.async_get_access_token() == first_refresh_response["access_token"]
        assert await auth.async_get_access_token() == second_refresh_response["access_token"]

    async def test_get_config_4xx(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Test that 4xx errors are swallowed with the error cause captured.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_data(
            status=400, response_data="invalid request")

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        except RuntimeError as e:
            # Validate that the underlying client response error is available for debugging
            assert isinstance(e.__cause__, ClientResponseError)

    async def test_get_config_5xx(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Test that 5xx errors are swallowed with the error cause captured.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_data(
            status=500, response_data="internal server error")

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        except RuntimeError as e:
            # Validate that the underlying client response error is available for debugging
            assert isinstance(e.__cause__, ClientResponseError)

    async def test_login_5xx(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Test that 5xx errors are swallowed with the error cause captured.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login(TEST_EMAIL_ADDRESS, TEST_PASSWORD).respond_with_data(
            status=500, response_data="internal error")

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        except RuntimeError as e:
            # Validate that the underlying client response error is available for debugging
            assert isinstance(e.__cause__, ClientResponseError)

    async def test_invalid_email(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Test that an invaid email response is converted to an AuthenticationError.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login("invalid-email", TEST_PASSWORD).respond_with_json(status=400, response_json={
            # From actual request
            "error": {
                "code": 400,
                "message": "INVALID_EMAIL",
                "errors": [
                    {
                        "message": "INVALID_EMAIL",
                        "domain": "global",
                        "reason": "invalid"
                    }
                ]
            }
        })

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth("invalid-email", TEST_PASSWORD)
        except AuthenticationError as e:
            assert e.reason == AuthenticationErrorReason.INVALID_EMAIL

    async def test_email_not_found(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Test that an unknown email address is converted to an AuthenticationError.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login("unknown@example.com", TEST_PASSWORD).respond_with_json(status=400, response_json={
            # From actual response
            "error": {
                "code": 400,
                "message": "EMAIL_NOT_FOUND",
                "errors": [
                    {
                        "message": "EMAIL_NOT_FOUND",
                        "domain": "global",
                        "reason": "invalid"
                    }
                ]
            }
        })

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth("unknown@example.com", TEST_PASSWORD)
        except AuthenticationError as e:
            assert e.reason == AuthenticationErrorReason.EMAIL_NOT_FOUND

    async def test_invalid_password(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Test that an invalid password response is converted to an AuthenticationError
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login(TEST_EMAIL_ADDRESS, "invalid-password").respond_with_json(status=400, response_json={
            "error": {
                "code": 400,
                "message": "INVALID_PASSWORD",
                "errors": [
                    {
                        "message": "INVALID_PASSWORD",
                        "domain": "global",
                        "reason": "invalid"
                    }
                ]
            }
        })

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth(TEST_EMAIL_ADDRESS, "invalid-password")
        except AuthenticationError as e:
            assert e.reason == AuthenticationErrorReason.INVALID_PASSWORD

    def test_authfactory_none_websession(self):
        """
        Test that AuthFactory cannot be created without a ClientSession
        """
        with pytest.raises(AssertionError):
            AuthFactory(websession=None)

    async def test_request_refresh_token(self, auth_test_object: AuthTestObject, client_session: ClientSession):
        """
        Test that the Auth object correctly refreshes the access token when executing a request.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        # if the token expires in less than 60 seconds it should get refreshed when `async_get_access_token` is called
        auth_test_object.expect_login(TEST_EMAIL_ADDRESS, TEST_PASSWORD).respond_with_json(
            LOGIN_RETURN_VALUE | {"expiresIn": "10"})
        auth_test_object.expect_token_refresh(
            LOGIN_RETURN_VALUE["refreshToken"]).respond_with_json(TOKEN_REFRESH_RETURN_VALUE)
        headers = {
            "Authorization": f"Bearer {TOKEN_REFRESH_RETURN_VALUE['access_token']}",
        }
        auth_test_object.expect_request("test", headers=headers).respond_with_json({"test": "test"})

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        auth = await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        respose = await auth.request("GET", "test")
        assert await respose.json() == {"test": "test"}