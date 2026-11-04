"""Client for the supported ThermoWorks Cloud integrations API."""

from __future__ import annotations

from datetime import datetime, timezone
import math
from email.utils import parsedate_to_datetime
from typing import Any

from aiohttp import ClientError, ClientSession, ClientTimeout

from .models.device import Device, Fan
from .models.device_channel import Alarm, DeviceChannel


class IntegrationsApiError(Exception):
    """Base error for the ThermoWorks integrations API."""


class IntegrationsAuthenticationError(IntegrationsApiError):
    """The API key was rejected."""


class IntegrationsRateLimitError(IntegrationsApiError):
    """The API requested that the caller wait before retrying."""

    def __init__(self, message: str, retry_after: float | None = None) -> None:
        super().__init__(message)
        self.retry_after = retry_after


class ThermoworksIntegrationsClient:
    """Read device data using a ThermoWorks integrations API key."""

    BASE_URL = "https://cloud.thermoworks.com/api"

    def __init__(
        self,
        websession: ClientSession,
        api_key: str,
        base_url: str | None = None,
    ) -> None:
        if not api_key or not api_key.strip():
            raise ValueError("api_key cannot be empty")
        self._websession = websession
        self._api_key = api_key.strip()
        self._base_url = (base_url or self.BASE_URL).rstrip("/")
        self._etag: str | None = None
        self._devices: list[Device] | None = None
        self._channels: dict[str, list[DeviceChannel]] = {}

    async def get_me(self) -> dict[str, Any]:
        """Validate the API key and return the API's metadata response."""
        return await self._request_json("/v1/me")

    async def get_devices(self) -> list[Device]:
        """Fetch all devices and cache their nested channel data."""
        headers: dict[str, str] = {}
        if self._etag:
            headers["If-None-Match"] = self._etag
        response = await self._request("/v1/devices", headers=headers)
        if response.status == 304:
            if self._devices is None:
                raise IntegrationsApiError("API returned 304 without a cached device snapshot")
            return self._devices

        payload = await self._read_json(response)
        if not isinstance(payload, dict) or not isinstance(payload.get("devices"), list):
            raise IntegrationsApiError("API response is missing its devices array")

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
        except (KeyError, TypeError, ValueError) as err:
            raise IntegrationsApiError("Invalid device data in API response") from err

        self._etag = response.headers.get("ETag")
        self._devices = devices
        self._channels = channels
        return devices

    def get_device_channels(self, device_identifier: str) -> list[DeviceChannel]:
        """Return channels from the most recent device snapshot."""
        return self._channels.get(device_identifier, [])

    async def _request_json(self, path: str) -> dict[str, Any]:
        response = await self._request(path)
        payload = await self._read_json(response)
        if not isinstance(payload, dict):
            raise IntegrationsApiError("API response is not a JSON object")
        return payload

    async def _request(self, path: str, headers: dict[str, str] | None = None):
        request_headers = {
            "Authorization": f"Bearer {self._api_key}",
            "Accept": "application/json",
        }
        if headers:
            request_headers.update(headers)
        try:
            response = await self._websession.get(
                f"{self._base_url}{path}",
                headers=request_headers,
                timeout=ClientTimeout(total=30),
            )
        except (ClientError, TimeoutError) as err:
            raise IntegrationsApiError("Unable to reach the ThermoWorks API") from err

        if response.status in (401, 403):
            await response.release()
            raise IntegrationsAuthenticationError("ThermoWorks API key was rejected")
        if response.status == 429:
            retry_after = _retry_after(response.headers.get("Retry-After"))
            await response.release()
            raise IntegrationsRateLimitError(
                "ThermoWorks API rate limit exceeded", retry_after
            )
        if response.status not in (200, 304):
            status = response.status
            await response.release()
            raise IntegrationsApiError(f"ThermoWorks API returned HTTP {status}")
        return response

    @staticmethod
    async def _read_json(response) -> Any:
        try:
            return await response.json()
        except (TypeError, ValueError) as err:
            raise IntegrationsApiError("ThermoWorks API returned invalid JSON") from err
        finally:
            response.release()


def _timestamp(value: Any) -> datetime | None:
    if value is None:
        return None
    result = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if result.tzinfo is None:
        result = result.replace(tzinfo=timezone.utc)
    return result


def _parse_alarm(value: dict[str, Any] | None, units: str | None) -> Alarm | None:
    if value is None:
        return None
    return Alarm(
        enabled=value.get("enabled"),
        alarming=value.get("alarming"),
        value=value.get("value"),
        units=units,
    )


def _parse_fan(value: dict[str, Any] | None) -> Fan | None:
    if value is None:
        return None
    return Fan(
        connected=value.get("connected"),
        connection=value.get("connected"),
        fan_channel=value.get("channel"),
        set_temp=value.get("setTemp"),
        state=value.get("state"),
    )


def _parse_device(raw: dict[str, Any]) -> tuple[Device, list[DeviceChannel]]:
    channels = [_parse_channel(channel) for channel in raw["channels"]]
    device = Device(
        device_id=raw.get("id"),
        serial=raw.get("serial"),
        label=raw.get("label"),
        type=raw.get("type"),
        device_name=raw.get("model") or raw.get("type"),
        device_display_units=raw.get("displayUnits"),
        firmware=raw.get("firmware"),
        battery=raw.get("battery"),
        battery_state=raw.get("batteryState"),
        fan=_parse_fan(raw.get("fan")),
        wifi_strength=raw.get("wifiSignal"),
        gateway_rssi=raw.get("gatewaySignal"),
        last_seen=_timestamp(raw.get("lastSeen")),
        transmit_interval_in_seconds=raw.get("transmitIntervalSeconds"),
    )
    return device, channels


def _parse_channel(raw: dict[str, Any]) -> DeviceChannel:
    units = raw.get("units")
    channel = DeviceChannel(
        number=str(raw["number"]) if raw.get("number") is not None else raw["id"],
        label=raw.get("label"),
        type=raw.get("type"),
        value=raw.get("value"),
        units=units,
        status=raw.get("status"),
        last_telemetry_saved=_timestamp(raw.get("lastTelemetrySaved")),
        alarm_high=_parse_alarm(raw.get("alarmHigh"), units),
        alarm_low=_parse_alarm(raw.get("alarmLow"), units),
        additional_properties={
            key: raw[key]
            for key in ("enabled", "probeFailed", "alarming")
            if key in raw
        } or None,
    )
    return channel


def _retry_after(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        seconds = float(value)
        return seconds if math.isfinite(seconds) else None
    except ValueError:
        try:
            return max(0.0, (parsedate_to_datetime(value) - datetime.now(timezone.utc)).total_seconds())
        except (TypeError, ValueError, OverflowError):
            return None
