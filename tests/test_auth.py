"""Test suite for the Auth object."""

from aiohttp import ClientSession, ClientResponseError
import pytest

from tests.auth_test_object import AuthTestObject
from tests.test_data import (
    CONFIG_RETURN_VALUE,
    LOGIN_RETURN_VALUE,
    TEST_EMAIL_ADDRESS,
    TEST_PASSWORD,
    TEST_USER_ID,
    TOKEN_REFRESH_RETURN_VALUE,
)
from thermoworks_cloud import (
    AuthFactory,
    AuthenticationError,
    AuthenticationErrorReason,
)


class TestAuth:
    """Test the Auth object."""

    async def test_build_auth(
        self, auth_test_object: AuthTestObject, client_session: ClientSession
    ):
        """Test the happy path for building an auth object."""

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login(
            TEST_EMAIL_ADDRESS, TEST_PASSWORD
        ).respond_with_json(LOGIN_RETURN_VALUE)

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        auth = await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        assert auth.user_id == TEST_USER_ID

    async def test_get_config_4xx(
        self, auth_test_object: AuthTestObject, client_session: ClientSession
    ):
        """Test that 4xx errors are swallowed with the error cause captured."""

        # Setup mock responses
        auth_test_object.expect_config().respond_with_data(
            status=400, response_data="invalid request"
        )

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        except RuntimeError as e:
            # Validate that the underlying client response error is available for debugging
            assert isinstance(e.__cause__, ClientResponseError)

    async def test_get_config_5xx(
        self, auth_test_object: AuthTestObject, client_session: ClientSession
    ):
        """Test that 5xx errors are swallowed with the error cause captured."""

        # Setup mock responses
        auth_test_object.expect_config().respond_with_data(
            status=500, response_data="internal server error"
        )

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        except RuntimeError as e:
            # Validate that the underlying client response error is available for debugging
            assert isinstance(e.__cause__, ClientResponseError)

    async def test_login_5xx(
        self, auth_test_object: AuthTestObject, client_session: ClientSession
    ):
        """Test that 5xx errors are swallowed with the error cause captured."""

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login(
            TEST_EMAIL_ADDRESS, TEST_PASSWORD
        ).respond_with_data(status=500, response_data="internal error")

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        except RuntimeError as e:
            # Validate that the underlying client response error is available for debugging
            assert isinstance(e.__cause__, ClientResponseError)

    async def test_invalid_email(
        self, auth_test_object: AuthTestObject, client_session: ClientSession
    ):
        """Test that an invaid email response is converted to an AuthenticationError."""

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login("invalid-email", TEST_PASSWORD).respond_with_json(
            status=400,
            response_json={
                # From actual request
                "error": {
                    "code": 400,
                    "message": "INVALID_EMAIL",
                    "errors": [
                        {
                            "message": "INVALID_EMAIL",
                            "domain": "global",
                            "reason": "invalid",
                        }
                    ],
                }
            },
        )

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth("invalid-email", TEST_PASSWORD)
        except AuthenticationError as e:
            assert e.reason == AuthenticationErrorReason.INVALID_EMAIL

    async def test_email_not_found(
        self, auth_test_object: AuthTestObject, client_session: ClientSession
    ):
        """Test that an unknown email address is converted to an AuthenticationError."""

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login(
            "unknown@example.com", TEST_PASSWORD
        ).respond_with_json(
            status=400,
            response_json={
                # From actual response
                "error": {
                    "code": 400,
                    "message": "EMAIL_NOT_FOUND",
                    "errors": [
                        {
                            "message": "EMAIL_NOT_FOUND",
                            "domain": "global",
                            "reason": "invalid",
                        }
                    ],
                }
            },
        )

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth("unknown@example.com", TEST_PASSWORD)
        except AuthenticationError as e:
            assert e.reason == AuthenticationErrorReason.EMAIL_NOT_FOUND

    async def test_invalid_password(
        self, auth_test_object: AuthTestObject, client_session: ClientSession
    ):
        """Test that an invalid password response is converted to an AuthenticationError"""

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login(
            TEST_EMAIL_ADDRESS, "invalid-password"
        ).respond_with_json(
            status=400,
            response_json={
                "error": {
                    "code": 400,
                    "message": "INVALID_PASSWORD",
                    "errors": [
                        {
                            "message": "INVALID_PASSWORD",
                            "domain": "global",
                            "reason": "invalid",
                        }
                    ],
                }
            },
        )

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth(TEST_EMAIL_ADDRESS, "invalid-password")
        except AuthenticationError as e:
            assert e.reason == AuthenticationErrorReason.INVALID_PASSWORD

    async def test_unknown_error(
            self, auth_test_object: AuthTestObject, client_session: ClientSession
    ):
        """Test that a response with an invalid error reason is converted 
        to an AuthenticationError.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)
        auth_test_object.expect_login(
            TEST_EMAIL_ADDRESS, TEST_PASSWORD
        ).respond_with_json(
            status=400,
            response_json={
                "error": {
                    "code": 400,
                    "message": "UKNOWN_ERROR_MESSAGE",
                    "errors": [
                        {
                            "message": "UKNOWN_ERROR_MESSAGE",
                            "domain": "global",
                            "reason": "unknown-reason",
                        }
                    ],
                }
            },
        )

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        try:
            await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        except AuthenticationError as e:
            assert e.reason == AuthenticationErrorReason.UNKNOWN

    def test_authfactory_none_websession(self):
        """Test that AuthFactory cannot be created without a ClientSession."""

        with pytest.raises(ValueError):
            AuthFactory(websession=None)

    async def test_request_refresh_token(
        self, auth_test_object: AuthTestObject, client_session: ClientSession
    ):
        """Test that the Auth object correctly refreshes the access token when 
        executing a request.
        """

        # Setup mock responses
        auth_test_object.expect_config().respond_with_json(CONFIG_RETURN_VALUE)

        # if the token expires in less than 60 seconds it should get refreshed
        # when `async_get_access_token` is called
        auth_test_object.expect_login(
            TEST_EMAIL_ADDRESS, TEST_PASSWORD
        ).respond_with_json(LOGIN_RETURN_VALUE | {"expiresIn": "10"})
        auth_test_object.expect_token_refresh(
            LOGIN_RETURN_VALUE["refreshToken"]
        ).respond_with_json(TOKEN_REFRESH_RETURN_VALUE)
        headers = {
            "Authorization": f"Bearer {TOKEN_REFRESH_RETURN_VALUE['access_token']}",
        }
        auth_test_object.expect_request("test", headers=headers).respond_with_json(
            {"test": "test"}
        )

        # act
        auth_factory = AuthFactory(client_session)

        # assert
        auth = await auth_factory.build_auth(TEST_EMAIL_ADDRESS, TEST_PASSWORD)
        respose = await auth.request("GET", "test")
        assert await respose.json() == {"test": "test"}
