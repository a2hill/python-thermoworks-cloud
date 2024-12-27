"""Manage authentication for the Thermoworks Cloud API."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Protocol, TypedDict, cast

from aiohttp import ClientResponse, ClientResponseError, ClientSession

from .models.user_credentials import UserCredentials, UserLoginResponse

class Auth(Protocol):
    """
    Interface for making authenticated requests.
    """
    @property
    def user_id(self) -> str:
        ...
        
    async def async_get_access_token(self) -> str:
        ...

    async def request(self, method, url, **kwargs) -> ClientResponse:
        ...

class _AuthBase(ABC, Auth):
    """Abstract class to make authenticated requests."""

    def __init__(self, websession: ClientSession, host: str, api_key: str) -> None:
        """Initialize the auth."""
        self.websession = websession
        self.host = host
        self.api_key = api_key

    @abstractmethod
    async def async_get_access_token(self) -> str:
        """Return a valid access token."""

    async def request(self, method, url) -> ClientResponse:
        """Make a request."""

        access_token = await self.async_get_access_token()
        headers = {
            "authorization": f"Bearer {access_token}"
        }
        url = f"{self.host}/{url}?key={self.api_key}"

        return await self.websession.request(
            method,
            url,
            headers=headers,
        )


def is_expired(expiration_time, buffer_seconds=60):
    """Determine if the key needs renewal based on a buffer time.

    Args:
        expiration_time (datetime): The calculated expiration time of the key.
        buffer_seconds (int): Time before expiration to renew the key (default is 60 seconds).

    Returns:
        bool: True if the key needs renewal, False otherwise.

    """
    # Get the current time
    current_time = datetime.now()
    experation_threshold = expiration_time - timedelta(seconds=buffer_seconds)

    # Check if the key is within the renewal buffer time
    return current_time >= experation_threshold


class WebConfigResponse(TypedDict):
    """Similar to <https://firebase.google.com/docs/reference/firebase-management/rest/v1beta1/projects>."""

    projectId: str
    appId: str
    databaseURL: str
    storageBucket: str
    locationId: str
    authDomain: str
    messagingSenderId: str
    measurementId: str


class FirestoreError(TypedDict):
    """See <https://firebase.google.com/docs/reference/rest/auth#section-error-format>."""

    message: str
    domain: str
    reason: str


class ErrorResponse(TypedDict):
    """See <https://firebase.google.com/docs/reference/rest/auth#section-error-format>."""

    code: int
    message: str
    errors: list[FirestoreError]


class AuthenticationErrorReason(Enum):
    """From <https://firebase.google.com/docs/reference/rest/auth?authuser=0#section-sign-in-email-password>."""

    INVALID_EMAIL = "INVALID_EMAIL"
    EMAIL_NOT_FOUND = "EMAIL_NOT_FOUND"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    USER_DISABLED = "USER_DISABLED"


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""

    def __init__(
        self,
        message: str,
        reason: AuthenticationErrorReason,
        details: list[FirestoreError],
    ) -> None:
        """Initialize an authentication error."""

        super().__init__(f"Error authenticating with Firestore: {reason.value}")
        self.message = message
        self.reason = reason
        self.details = details


class _TokenManager:
    """Manage access tokens for Auth."""

    _IDENTITY_HOST = "https://identitytoolkit.googleapis.com"
    _TOKEN_HOST = "https://securetoken.googleapis.com"

    _user_credentials: UserCredentials


    def __init__(self, websession: ClientSession, api_key: str) -> None:
        """Initialize token manager."""
        self._websession = websession
        self._api_key = api_key

    async def login(self, email: str, password: str) -> None:
        """Exchange login credentials for token credentials."""

        url = f"{self._IDENTITY_HOST}/v1/accounts:signInWithPassword"
        query = {"key": self._api_key}
        headers = {"Content-Type": "application/json"}
        json = {
            "email": email,
            "password": password,
            "returnSecureToken": True,
        }

        response = await self._websession.request(
            "post", url, headers=headers, json=json, params=query
        )

        if response.ok:
            login_response = await response.json()
            cast(UserLoginResponse, login_response)
            self._user_credentials = UserCredentials.from_user_login_response(
                login_response
            )
        elif response.status == 400:
            login_response = await response.json()
            if login_response["error"]:
                error_response = cast(ErrorResponse, login_response["error"])
                error_message = error_response["message"]
                error_details = error_response["errors"]

                if error_message in AuthenticationErrorReason._value2member_map_:
                    raise AuthenticationError(
                        message=f"Authentication failed: {error_message}",
                        reason=AuthenticationErrorReason(error_message),
                        details=error_details,
                    )
        else:
            try:
                response.raise_for_status()
            except ClientResponseError as e:
                raise RuntimeError("Unable to authenticate") from e

    @property
    def user_id(self) -> str:
        """Return id of the user that the manager is authenticate with."""
        return self._user_credentials.user_id

    @property
    def access_token(self) -> str:
        """Return an access token for use with Auth."""
        return self._user_credentials.access_token

    def is_token_valid(self) -> bool:
        """Return a bool indicating whether the token is expired."""

        return not is_expired(self._user_credentials.expiration_time)

    async def refresh_access_token(self) -> None:
        """Refresh the access token."""

        url = f"{self._TOKEN_HOST}/v1/token?key={self._api_key}"
        headers = {"Content-Type": "application/json"}
        json = {
            "grant_type": "refresh_token",
            "refresh_token": self._user_credentials.refresh_token,
        }

        response = await self._websession.request(
            "post", url, headers=headers, json=json
        )
        response.raise_for_status()
        refresh_token_response = await response.json()
        self._user_credentials = UserCredentials.from_refresh_token_response(
            refresh_token_response
        )


class _Auth(_AuthBase):
    """Execute authenticated requests."""

    def __init__(
        self,
        websession: ClientSession,
        api_url_root: str,
        api_key: str,
        token_manager: _TokenManager,
    ) -> None:
        """Initialize the auth."""
        super().__init__(websession, api_url_root, api_key)
        self.token_manager = token_manager

    @property
    def user_id(self) -> str:
        """The id of the user that is authenticated."""
        return self.token_manager.user_id

    async def async_get_access_token(self) -> str:
        """Return a valid access token."""
        if self.token_manager.is_token_valid():
            return self.token_manager.access_token

        await self.token_manager.refresh_access_token()
        return self.token_manager.access_token


class AuthFactory:
    """Create Auth objects."""

    _API_KEY = "AIzaSyCf079iccUFc1k7VHdGXng22zXDy8Y3KEY"
    _APP_ID = "1:78998049458:web:b41e9d405d8c7de95eefab"
    _FIREBASE_HOST = "https://firebase.googleapis.com"
    _FIRESTORE_HOST = "https://firestore.googleapis.com"

    _config: WebConfigResponse

    def __init__(self, websession: ClientSession) -> None:
        """Initialize the factory."""

        assert websession is not None, "parameter cannot be None"
        self._websession = websession

    async def get_config(self) -> None:
        """Get the Firestore project information for this application."""

        url = f"{self._FIREBASE_HOST}/v1alpha/projects/-/apps/{self._APP_ID}/webConfig"
        headers = {
            "accept": "application/json",
            "x-goog-api-key": self._API_KEY,
        }

        try:
            response = await self._websession.request("get", url, headers=headers)
            response.raise_for_status()
            self._config: WebConfigResponse = await response.json()
        except Exception as e:
            raise RuntimeError("Unable to fetch application configuration") from e

    async def build_auth(self, email: str, password: str) -> Auth:
        """Build an Auth instance."""

        await self.get_config()

        token_manager = _TokenManager(self._websession, self._API_KEY)
        await token_manager.login(email, password)
        return _Auth(
            self._websession,
            api_url_root=f"{self._FIRESTORE_HOST}/v1/projects/{self._config['projectId']}/databases/(default)/documents",
            api_key=self._API_KEY,
            token_manager=token_manager,
        )