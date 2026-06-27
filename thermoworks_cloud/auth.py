"""Manage authentication for the Thermoworks Cloud API."""

from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from enum import Enum
from typing import Protocol, TypedDict, cast

from aiohttp import ClientResponse, ClientResponseError, ClientSession

from .models.user_credentials import _UserCredentials, _UserLoginResponse


class Auth(Protocol):
    """Interface to make authenticated HTTP requests to the ThermoWorks Cloud service."""

    @property
    def user_id(self) -> str:
        """The id of the logged in user"""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def storage_bucket(self) -> str:
        """The Firebase Storage bucket configured for this application."""
        ...  # pylint: disable=unnecessary-ellipsis

    @property
    def storage_url_root(self) -> str:
        """The Firebase Storage API root URL configured for this application."""
        ...  # pylint: disable=unnecessary-ellipsis

    async def request(
        self, method, url, additional_headers=None, json=None, params=None
    ) -> ClientResponse:
        """Make an authenticated request."""
        ...  # pylint: disable=unnecessary-ellipsis

    async def request_url(
        self, method, url, additional_headers=None, json=None, params=None
    ) -> ClientResponse:
        """Make an authenticated request to an absolute URL."""
        ...  # pylint: disable=unnecessary-ellipsis


class _AuthBase(ABC, Auth):
    """Abstract class to make authenticated requests."""

    def __init__(self, websession: ClientSession, host: str, api_key: str) -> None:
        """Initialize the auth."""
        self.websession = websession
        self.host = host
        self.api_key = api_key

    @abstractmethod
    async def _async_get_access_token(self) -> str:
        """Return a valid access token."""
        ...  # pylint: disable=unnecessary-ellipsis

    async def request(
        self, method, url, additional_headers=None, json=None, params=None
    ) -> ClientResponse:

        request_params = {"key": self.api_key}
        if params:
            request_params.update(params)

        return await self.request_url(
            method,
            f"{self.host}/{url}",
            additional_headers=additional_headers,
            json=json,
            params=request_params,
        )

    async def request_url(
        self, method, url, additional_headers=None, json=None, params=None
    ) -> ClientResponse:

        access_token = await self._async_get_access_token()
        headers = {"authorization": f"Bearer {access_token}"}

        # If headers are provided in kwargs, merge them with our auth headers
        if additional_headers:
            headers.update(additional_headers)

        return await self.websession.request(
            method,
            url,
            headers=headers,
            json=json,
            params=params
        )


def _is_expired(expiration_time, buffer_seconds=60):
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


class _WebConfigResponse(TypedDict):
    """See
    <https://firebase.google.com/docs/reference/firebase-management/rest/v1beta1/projects>.
    """

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
    """See
    <https://firebase.google.com/docs/reference/rest/auth?authuser=0#section-sign-in-email-password>.
    """

    INVALID_EMAIL = "INVALID_EMAIL"
    EMAIL_NOT_FOUND = "EMAIL_NOT_FOUND"
    INVALID_PASSWORD = "INVALID_PASSWORD"
    USER_DISABLED = "USER_DISABLED"
    UNKNOWN = "UNKNOWN"
    """Catch-all for any undocumented error reasons"""


class AuthenticationError(Exception):
    """Custom exception for authentication errors."""

    def __init__(
        self,
        message: str,
        reason: AuthenticationErrorReason,
        details: list[FirestoreError],
    ) -> None:
        """Initialize an authentication error."""

        super().__init__(
            f"Error authenticating with Firestore: {reason.value}")
        self.message = message
        self.reason = reason
        self.details = details


class _TokenManager:
    """Manage access tokens for Auth."""

    _IDENTITY_HOST = "https://identitytoolkit.googleapis.com"
    _TOKEN_HOST = "https://securetoken.googleapis.com"

    _user_credentials: _UserCredentials

    def __init__(self, websession: ClientSession, api_key: str,
                 referer: str = "https://cloud.thermoworks.com/") -> None:
        """Initialize token manager."""
        self._websession = websession
        self._api_key = api_key
        self._referer = referer

    async def login(self, email: str, password: str) -> None:
        """Exchange login credentials for token credentials."""

        url = f"{self._IDENTITY_HOST}/v1/accounts:signInWithPassword"
        query = {"key": self._api_key}
        headers = {
            "Content-Type": "application/json",
            "referer": self._referer
        }
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
            cast(_UserLoginResponse, login_response)
            self._user_credentials = _UserCredentials.from_user_login_response(
                login_response
            )
        elif response.status == 400:
            login_response = await response.json()
            if login_response["error"]:
                error_response = cast(ErrorResponse, login_response["error"])
                error_message = error_response["message"]
                error_details = error_response["errors"]

                try:
                    error_reason = AuthenticationErrorReason(error_message)
                except ValueError:
                    error_reason = AuthenticationErrorReason.UNKNOWN
                raise AuthenticationError(
                    message=f"Authentication failed: {error_message}",
                    reason=error_reason,
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

        return not _is_expired(self._user_credentials.expiration_time)

    async def refresh_access_token(self) -> None:
        """Refresh the access token."""

        url = f"{self._TOKEN_HOST}/v1/token?key={self._api_key}"
        headers = {
            "Content-Type": "application/json",
            "referer": self._referer
        }
        json = {
            "grant_type": "refresh_token",
            "refresh_token": self._user_credentials.refresh_token,
        }

        response = await self._websession.request(
            "post", url, headers=headers, json=json
        )
        response.raise_for_status()
        refresh_token_response = await response.json()
        self._user_credentials = _UserCredentials.from_refresh_token_response(
            refresh_token_response
        )


class _Auth(_AuthBase):
    """Execute authenticated requests."""

    def __init__(
        self,
        websession: ClientSession,
        api_url_root: str,
        api_key: str,
        storage_bucket: str,
        storage_url_root: str,
        token_manager: _TokenManager,
    ) -> None:
        """Initialize the auth."""
        super().__init__(websession, api_url_root, api_key)
        self._storage_bucket = storage_bucket
        self._storage_url_root = storage_url_root
        self.token_manager = token_manager

    @property
    def user_id(self) -> str:
        """The id of the user that is authenticated."""
        return self.token_manager.user_id

    @property
    def storage_bucket(self) -> str:
        """The Firebase Storage bucket configured for this application."""
        return self._storage_bucket

    @property
    def storage_url_root(self) -> str:
        """The Firebase Storage API root URL configured for this application."""
        return self._storage_url_root

    async def _async_get_access_token(self) -> str:
        """Return a valid access token."""
        if self.token_manager.is_token_valid():
            return self.token_manager.access_token

        await self.token_manager.refresh_access_token()
        return self.token_manager.access_token


class AuthFactory:  # pylint: disable=too-few-public-methods
    """Builds `thermoworks_cloud.Auth` objects."""

    _DEFAULT_API_KEY = "AIzaSyCf079iccUFc1k7VHdGXng22zXDy8Y3KEY"
    _DEFAULT_APP_ID = "1:78998049458:web:b41e9d405d8c7de95eefab"
    _DEFAULT_REFERER = "https://cloud.thermoworks.com/"
    _FIREBASE_HOST = "https://firebase.googleapis.com"
    _FIRESTORE_HOST = "https://firestore.googleapis.com"
    _FIREBASE_STORAGE_HOST = "https://firebasestorage.googleapis.com"

    def __init__(self, websession: ClientSession, api_key: str | None = None,
                 app_id: str | None = None, referer: str | None = None) -> None:
        """Initialize the auth factory.

        Args:
            websession (ClientSession): The HTTP client to be used when authenticating the user.
            api_key (str | None): Firebase API key. Defaults to ThermoWorks Cloud.
            app_id (str | None): Firebase app ID. Defaults to ThermoWorks Cloud.
            referer (str | None): Referer header value. Defaults to ThermoWorks Cloud.
        """

        if websession is None:
            raise ValueError("parameter cannot be None")

        self._websession = websession
        self._api_key = api_key or self._DEFAULT_API_KEY
        self._app_id = app_id or self._DEFAULT_APP_ID
        self._referer = referer or self._DEFAULT_REFERER

    async def _get_config(self) -> _WebConfigResponse:
        """Get the Firestore project information for this application."""

        url = f"{self._FIREBASE_HOST}/v1alpha/projects/-/apps/{self._app_id}/webConfig"
        headers = {
            "accept": "application/json",
            "x-goog-api-key": self._api_key,
            "referer": self._referer
        }

        try:
            response = await self._websession.request("get", url, headers=headers)
            response.raise_for_status()
            return await response.json()
        except Exception as e:
            raise RuntimeError(
                "Unable to fetch application configuration") from e

    async def build_auth(self, email: str, password: str) -> Auth:
        """Build an Auth instance.

        Args:
            email (str): The email address of a cloud user.
            password (str): The password for the user.

        Returns:
            Auth: An Auth object for making requests on behalf of the authenticated user.
        """

        web_config = await self._get_config()
        project_id = web_config["projectId"]
        url_root = f"{self._FIRESTORE_HOST}/v1/projects/{project_id}/databases/(default)"

        token_manager = _TokenManager(self._websession, self._api_key,
                                      referer=self._referer)
        await token_manager.login(email, password)
        return _Auth(
            self._websession,
            api_url_root=url_root,
            api_key=self._api_key,
            storage_bucket=web_config["storageBucket"],
            storage_url_root=self._FIREBASE_STORAGE_HOST,
            token_manager=token_manager,
        )
