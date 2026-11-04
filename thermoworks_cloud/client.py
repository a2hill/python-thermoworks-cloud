"""Accessor for the ThermoWorks Cloud API."""

from http import HTTPStatus
from typing import Dict, List, Optional, cast

from aiohttp import ClientResponse, ClientSession

from thermoworks_cloud.utils import format_client_response

from .models.account import Account, _json_to_account
from .models.device import Device, DevicesResponse, _json_to_device


class ApiAuthenticationError(Exception):
    """Custom exception indicating that the API key was rejected."""

    def __init__(self, message: str) -> None:
        """Initialize the error."""

        super().__init__(message)
        self.message: str = message


class RateLimitError(RuntimeError):
    """Custom exception indicating that the API key has used up its request budget."""

    def __init__(self, message: str, retry_after: Optional[int] = None) -> None:
        """Initialize the error.

        Args:
            message (str): A description of the error.
            retry_after (int | None): Seconds to wait before retrying, if the service said.
        """

        super().__init__(message)
        self.message: str = message
        self.retry_after: Optional[int] = retry_after


class ThermoworksClient:
    """Client for the ThermoWorks Cloud API.

    Requests count against a per-key rate limit, so `get_devices` is the only way to read
    devices for polling: it returns every device with its channels in a single request.
    """

    def __init__(self, websession: ClientSession, api_key: str, base_url: str) -> None:
        """Create a new client.

        Args:
            websession (ClientSession): The HTTP client used to make requests.
            api_key (str): An API key from the ThermoWorks Cloud web app.
            base_url (str): The root URL of the API. This differs between cloud providers.
        """
        self._websession: ClientSession = websession
        self._api_key: str = api_key
        self._base_url: str = base_url.rstrip("/")
        self._etag: Optional[str] = None
        self._devices: List[Device] = []

    async def get_me(self) -> Account:
        """Fetch information about the account and API key."""

        response = await self._request("v1/me")
        if response.ok:
            account_json = await response.json()
            return _json_to_account(account_json)

        raise await self._response_error("Failed to get account", response)

    async def get_devices(self) -> List[Device]:
        """Fetch all devices visible to the API key, including their channels.

        Sends the ETag of the previous response, which the service can answer with
        `304 Not Modified` to indicate that the previous devices are still current.
        """

        headers = {"If-None-Match": self._etag} if self._etag else None
        response = await self._request("v1/devices", additional_headers=headers)

        if response.status == HTTPStatus.NOT_MODIFIED:
            return self._devices

        if response.ok:
            devices_json = cast(DevicesResponse, await response.json())
            self._devices = [_json_to_device(device) for device in devices_json["devices"]]
            self._etag = response.headers.get("ETag")
            return self._devices

        raise await self._response_error("Failed to get devices", response)

    async def get_devices_raw(self) -> DevicesResponse:
        """Fetch the unparsed response of the devices API, for diagnosing unsupported devices.

        This always returns a full response, so it does not use or update the ETag.
        """

        response = await self._request("v1/devices")
        if response.ok:
            return cast(DevicesResponse, await response.json())

        raise await self._response_error("Failed to get devices", response)

    async def _request(
        self, path: str, additional_headers: Optional[Dict[str, str]] = None
    ) -> ClientResponse:
        """Make an authenticated request."""

        headers = {"authorization": f"Bearer {self._api_key}"}
        if additional_headers:
            headers.update(additional_headers)

        return await self._websession.request(
            "get", f"{self._base_url}/{path}", headers=headers
        )

    async def _response_error(self, message: str, response: ClientResponse) -> Exception:
        """Build the exception for a failed response."""

        if response.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            return ApiAuthenticationError("The API key was rejected")

        if response.status == HTTPStatus.TOO_MANY_REQUESTS:
            retry_after = response.headers.get("Retry-After")
            return RateLimitError(
                "The API key's rate limit was exceeded",
                int(retry_after) if retry_after else None,
            )

        try:
            error_response = await format_client_response(response)
        except RuntimeError:
            error_response = "Could not read response body."

        return RuntimeError(f"{message}: {error_response}")
