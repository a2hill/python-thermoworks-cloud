"""Client for the ThermoWorks Cloud API."""

from __future__ import annotations

from datetime import datetime, timezone
import math
from email.utils import parsedate_to_datetime
from typing import Any, Mapping

from aiohttp import ClientError, ClientSession, ClientTimeout, ContentTypeError

from .models.device import Device
from .models.device_channel import DeviceChannel
from .models.snapshot import _parse_device
from .core import ResourceNotFoundError


class ApiError(RuntimeError):
    """Base error for the ThermoWorks integrations API."""


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
    """Read device data using a ThermoWorks integrations API key."""

    def __init__(
        self,
        websession: ClientSession,
        api_key: str,
        base_url: str,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key cannot be empty")
        self._websession = websession
        self._api_key = api_key.strip()
        if not base_url:
            raise ValueError("base_url cannot be empty")
        self._base_url = base_url.rstrip("/")
        self._etag: str | None = None
        self._devices: list[Device] | None = None
        self._channels: dict[str, list[DeviceChannel]] = {}

    async def get_me(self) -> dict[str, Any]:
        """Validate the API key and return the API's metadata response."""
        payload = await self._request_json("/v1/me")
        if not isinstance(payload.get("accountId"), str) or not payload["accountId"]:
            raise MalformedResponseError("API response is missing its account ID")
        return payload

    async def get_devices(self) -> list[Device]:
        """Fetch all devices and cache their nested channel data."""
        headers: dict[str, str] = {}
        if self._etag:
            headers["If-None-Match"] = self._etag
        status, response_headers, payload = await self._request("/v1/devices", headers=headers)
        if status == 304:
            if self._devices is None:
                raise MalformedResponseError("API returned 304 without a cached device snapshot")
            return self._devices

        if not isinstance(payload, dict) or not isinstance(payload.get("devices"), list):
            raise MalformedResponseError("API response is missing its devices array")

        devices: list[Device] = []
        channels: dict[str, list[DeviceChannel]] = {}
        try:
            for raw_device in payload["devices"]:
                device, device_channels = _parse_device(raw_device)
                identifier = device.device_id or device.serial
                if not identifier:
                    raise ValueError("device is missing id and serial")
                devices.append(device)
                channels[identifier] = device_channels
        except (AttributeError, KeyError, TypeError, ValueError, OverflowError):
            raise MalformedResponseError("Invalid device data in API response") from None

        self._etag = response_headers.get("ETag")
        self._devices = devices
        self._channels = channels
        return devices

    def get_device_channels(self, device_identifier: str) -> list[DeviceChannel]:
        """Return channels from the most recent device snapshot."""
        return self._channels.get(device_identifier, [])

    async def get_device(self, device_serial: str) -> Device:
        """Fetch a device by serial number using the current API snapshot."""
        devices = await self.get_devices()
        for device in devices:
            if device.serial == device_serial or device.device_id == device_serial:
                return device
        raise ResourceNotFoundError("Device not found")

    async def get_device_channel(self, device_serial: str, channel: str) -> DeviceChannel:
        """Fetch a channel through the same interface as the Firebase client."""
        device = await self.get_device(device_serial)
        for device_channel in self.get_device_channels(device.device_id or device.serial):
            if device_channel.number == str(channel):
                return device_channel
        raise ResourceNotFoundError("Device channel not found")

    async def _request_json(self, path: str) -> dict[str, Any]:
        status, _, payload = await self._request(path)
        if status != 200 or not isinstance(payload, dict):
            raise MalformedResponseError("API response is not a JSON object")
        return payload

    async def _request(
        self, path: str, headers: dict[str, str] | None = None
    ) -> tuple[int, Mapping[str, str], Any]:
        request_headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }
        if headers:
            request_headers.update(headers)
        try:
            async with self._websession.get(
                f"{self._base_url}{path}",
                headers=request_headers,
                timeout=ClientTimeout(total=30),
                allow_redirects=False,
            ) as response:
                if response.status in (401, 403):
                    raise ApiAuthenticationError("ThermoWorks API key was rejected")
                if response.status == 429:
                    raise RateLimitError(
                        "ThermoWorks API rate limit exceeded",
                        _retry_after(response.headers.get("Retry-After")),
                    )
                if response.status not in (200, 304):
                    raise ApiError(f"ThermoWorks API returned HTTP {response.status}")
                payload = None
                if response.status == 200:
                    try:
                        payload = await response.json()
                    except (ContentTypeError, ValueError, TypeError):
                        raise MalformedResponseError(
                            "ThermoWorks API returned invalid JSON"
                        ) from None
                return response.status, response.headers, payload
        except (ClientError, TimeoutError):
            raise ApiError("Unable to reach the ThermoWorks API") from None


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
