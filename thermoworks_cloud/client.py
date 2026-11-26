"""Accessor for the ThermoWorks Cloud API."""

from http import HTTPStatus
from typing import Callable, Dict, List, Optional, cast

from aiohttp import ClientResponse, ClientSession

from thermoworks_cloud.utils import format_client_response

from .models.account import Account, RateLimitStatus, _json_to_account
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


class ThermoworksClient:  # pylint: disable=too-many-instance-attributes
    """Client for the ThermoWorks Cloud API.

    Requests count against a per-key rate limit, so `get_devices` is the only way to read
    devices for polling: it returns every device with its channels in a single request.

    Every response counts toward both the per-minute and the daily limit, including
    `304 Not Modified`. The service reports only the per-minute budget (see `rate_limit`), so a
    caller that tracks the daily budget counts responses itself with `on_response`.
    """

    def __init__(
        self,
        websession: ClientSession,
        api_key: str,
        base_url: str,
        on_response: Optional[Callable[[int], None]] = None,
    ) -> None:
        """Create a new client.

        Args:
            websession (ClientSession): The HTTP client used to make requests.
            api_key (str): An API key from the ThermoWorks Cloud web app.
            base_url (str): The root URL of the API. This differs between cloud providers.
            on_response (Callable[[int], None] | None): Called with the HTTP status of every
                response the service sends, whatever the status, before it is handled. Requests
                that get no response are not reported.
        """
        self._websession: ClientSession = websession
        self._api_key: str = api_key
        self._base_url: str = base_url.rstrip("/")
        self._on_response: Optional[Callable[[int], None]] = on_response
        self._etag: Optional[str] = None
        self._devices: List[Device] = []
        self._account: Optional[Account] = None
        self._rate_limit: Optional[RateLimitStatus] = None

    @property
    def account(self) -> Optional[Account]:
        """The account returned by the latest successful `get_me`, or None before one."""
        return self._account

    @property
    def rate_limit(self) -> Optional[RateLimitStatus]:
        """The per-minute budget from the latest response that reported it, or None before one."""
        return self._rate_limit

    async def get_me(self) -> Account:
        """Fetch information about the account and API key."""

        response = await self._request("v1/me")
        if response.ok:
            account_json = await response.json()
            self._account = _json_to_account(account_json)
            return self._account

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

        response = await self._websession.request(
            "get", f"{self._base_url}/{path}", headers=headers
        )

        rate_limit = RateLimitStatus(
            limit=_int_header(response, "X-RateLimit-Limit"),
            remaining=_int_header(response, "X-RateLimit-Remaining"),
            reset_seconds=_int_header(response, "X-RateLimit-Reset"),
        )
        if rate_limit != RateLimitStatus():
            self._rate_limit = rate_limit

        if self._on_response is not None:
            self._on_response(response.status)

        return response

    async def _response_error(self, message: str, response: ClientResponse) -> Exception:
        """Build the exception for a failed response."""

        if response.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
            return ApiAuthenticationError("The API key was rejected")

        if response.status == HTTPStatus.TOO_MANY_REQUESTS:
            return RateLimitError(
                "The API key's rate limit was exceeded",
                _int_header(response, "Retry-After"),
            )

        try:
            error_response = await format_client_response(response)
        except RuntimeError:
            error_response = "Could not read response body."

        return RuntimeError(f"{message}: {error_response}")


def _int_header(response: ClientResponse, name: str) -> Optional[int]:
    """Return a header as a whole number, or None when it is missing or not a number."""

    value = response.headers.get(name)
    try:
        return int(value) if value is not None else None
    except ValueError:
        return None
