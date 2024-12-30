"""Model for User Credentials for Firestore."""

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import TypedDict


class _UserLoginResponse(TypedDict):
    """See:
    <https://firebase.google.com/docs/reference/rest/auth#section-sign-in-email-password>.
    """

    kind: str
    localId: str
    email: str
    displayName: str
    idToken: str
    registered: bool
    refreshToken: str
    expiresIn: str


class _RefreshTokenResponse(TypedDict):
    """See:
    <https://firebase.google.com/docs/reference/rest/auth#section-refresh-token>.
    """

    access_token: str
    expires_in: str
    token_type: str
    refresh_token: str
    id_token: str
    user_id: str
    project_id: str


def _get_expiration_time(seconds_until_expiration: int):
    """Calculate the exact expiration time of a key.

    Args:
        seconds_until_expiration (int): Number of seconds until the key expires.

    Returns:
        datetime: The expiration time.

    """
    # Get the current time
    current_time = datetime.now()

    # Calculate the expiration time
    return current_time + timedelta(seconds=seconds_until_expiration)


@dataclass
class _UserCredentials:
    """Internal representation of credentials for a user."""

    user_id: str
    access_token: str
    refresh_token: str
    expiration_time: datetime

    @staticmethod
    def from_user_login_response(response: _UserLoginResponse) -> "_UserCredentials":
        """Create UserCredentials from the login API response."""
        return _UserCredentials(
            user_id=response["localId"],
            access_token=response["idToken"],
            refresh_token=response["refreshToken"],
            expiration_time=_get_expiration_time(int(response["expiresIn"])),
        )

    @staticmethod
    def from_refresh_token_response(
        response: _RefreshTokenResponse,
    ) -> "_UserCredentials":
        """Create UserCredentials from the refresh token API response."""
        return _UserCredentials(
            user_id=response["user_id"],
            access_token=response["access_token"],
            refresh_token=response["refresh_token"],
            expiration_time=_get_expiration_time(int(response["expires_in"])),
        )
