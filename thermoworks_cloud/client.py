"""Client for the ThermoWorks Cloud API."""

from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from http import HTTPStatus
import json
import math

from aiohttp import ClientError, ClientResponse, ClientSession, ClientTimeout, ContentTypeError

from .core import ResourceNotFoundError
from .models.account import Account, _api_to_account
from .models.device import Device, _api_to_device
from .models.device_channel import DeviceChannel, _api_to_device_channel


class ApiError(RuntimeError):
    """Base error for the ThermoWorks API."""


class MalformedResponseError(ApiError):
    """The service returned an invalid response."""


class ApiAuthenticationError(ApiError):
    """The API key was rejected."""


class RateLimitError(ApiError):
    """The API requested that the caller wait before retrying."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class ThermoworksClient:
    """Read devices with an API key and a provider-supplied endpoint."""

    def __init__(self, websession: ClientSession, api_key: str, base_url: str) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key cannot be empty")
        if not base_url or not base_url.strip():
            raise ValueError("base_url cannot be empty")
        self._websession = websession
        self._api_key = api_key.strip()
        self._base_url = base_url.rstrip("/")
        self._etag: str | None = None
        self._devices: list[Device] | None = None
        self._channels: dict[str, list[DeviceChannel]] = {}

    async def get_me(self) -> Account:
        """Fetch account metadata and validate the API key."""
        response = await self._request("/v1/me")
        try:
            if response.ok and response.status != HTTPStatus.NOT_MODIFIED:
                payload = await response.json()
                return _api_to_account(payload)
            raise MalformedResponseError("Unexpected empty account response")
        except (ContentTypeError, json.JSONDecodeError):
            raise MalformedResponseError("ThermoWorks API returned invalid JSON") from None
        except ValueError:
            # Converters raise ValueError only for explicitly validated API fields.
            raise MalformedResponseError("Invalid account data in API response") from None
        except (ClientError, TimeoutError):
            raise ApiError("Unable to read the ThermoWorks API response") from None
        finally:
            response.release()

    async def get_devices(self) -> list[Device]:
        """Fetch one device/channel snapshot; retain it when the ETag is unchanged."""
        headers = {"If-None-Match": self._etag} if self._etag else None
        response = await self._request("/v1/devices", headers)
        try:
            # Unlike a successful JSON response, a conditional 304 has no body.
            if response.status == HTTPStatus.NOT_MODIFIED:
                if self._devices is None:
                    raise MalformedResponseError(
                        "API returned 304 without a cached device snapshot"
                    )
                return self._devices
            if response.ok:
                payload = await response.json()
                if not isinstance(payload, dict) or not isinstance(payload.get("devices"), list):
                    raise MalformedResponseError("API response is missing its devices array")
                devices: list[Device] = []
                channels: dict[str, list[DeviceChannel]] = {}
                for raw_device in payload["devices"]:
                    device = _api_to_device(raw_device)
                    raw_channels = raw_device.get("channels")
                    if not isinstance(raw_channels, list):
                        raise ValueError("Device channels must be an array")
                    if device.device_id in channels:
                        raise ValueError("Duplicate device ID")
                    channels[device.device_id] = [
                        _api_to_device_channel(channel) for channel in raw_channels
                    ]
                    devices.append(device)
                # Commit the ETag and models together, only after the entire response validates.
                self._etag = response.headers.get("ETag")
                self._devices = devices
                self._channels = channels
                return devices
            raise ApiError("Unable to fetch devices")
        except (ContentTypeError, json.JSONDecodeError):
            raise MalformedResponseError("ThermoWorks API returned invalid JSON") from None
        except ValueError:
            raise MalformedResponseError("Invalid device data in API response") from None
        except (ClientError, TimeoutError):
            raise ApiError("Unable to read the ThermoWorks API response") from None
        finally:
            response.release()

    def get_device_channels(self, device_identifier: str) -> list[DeviceChannel]:
        """Return channels for an authoritative API device ID from the latest snapshot."""
        return self._channels.get(device_identifier, [])

    async def get_device(self, device_serial: str) -> Device:
        """Fetch a device by serial or ID through the existing client interface."""
        for device in await self.get_devices():
            if device.serial == device_serial or device.device_id == device_serial:
                return device
        raise ResourceNotFoundError("Device not found")

    async def get_device_channel(self, device_serial: str, channel: str) -> DeviceChannel:
        """Fetch a channel by its legacy channel number."""
        device = await self.get_device(device_serial)
        for device_channel in self.get_device_channels(device.device_id):
            if device_channel.number == str(channel):
                return device_channel
        raise ResourceNotFoundError("Device channel not found")

    async def _request(self, path: str, headers: dict[str, str] | None = None) -> ClientResponse:
        """Return the aiohttp response, matching the existing client's request boundary.

        Callers own JSON decoding, model conversion, and response release. Error
        responses are released here; response bodies and transport exception text
        are deliberately excluded from errors because either may contain credentials.
        """
        request_headers = {"Authorization": f"Bearer {self._api_key}", "Accept": "application/json"}
        if headers:
            request_headers.update(headers)
        try:
            response = await self._websession.request(
                "get",
                f"{self._base_url}{path}",
                headers=request_headers,
                timeout=ClientTimeout(total=30),
                allow_redirects=False,
            )
        except (ClientError, TimeoutError):
            raise ApiError("Unable to reach the ThermoWorks API") from None
        if response.status == HTTPStatus.NOT_MODIFIED:
            return response
        if response.ok and response.status < HTTPStatus.MULTIPLE_CHOICES:
            return response
        try:
            if response.status in (HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN):
                raise ApiAuthenticationError("ThermoWorks API key was rejected")
            if response.status == HTTPStatus.TOO_MANY_REQUESTS:
                raise RateLimitError(
                    "ThermoWorks API rate limit exceeded",
                    _retry_after(response.headers.get("Retry-After")),
                )
            raise ApiError(f"ThermoWorks API returned HTTP {response.status}")
        finally:
            response.release()


def _retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        seconds = float(value)
        return max(0.0, seconds) if math.isfinite(seconds) else None
    except ValueError:
        try:
            return max(
                0.0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds()
            )
        except (TypeError, ValueError, OverflowError):
            return None
