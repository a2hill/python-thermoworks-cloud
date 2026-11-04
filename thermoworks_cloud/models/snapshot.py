"""Map API snapshots to the existing device and channel models."""

from datetime import datetime, timezone
from typing import Any

from .device import Device, Fan
from .device_channel import Alarm, DeviceChannel


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
            key: raw[key] for key in ("enabled", "probeFailed", "alarming") if key in raw
        }
        or None,
    )
    return channel
