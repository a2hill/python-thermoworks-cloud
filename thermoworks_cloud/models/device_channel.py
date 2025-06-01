"""Classes related to a DeviceChannel."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

from thermoworks_cloud.utils import parse_datetime, unwrap_firestore_value, get_field_value


@dataclass
class Reading:
    """A temperature reading from a device channel."""

    value: Optional[float] = None
    """"The temperature units as a string like "F" """
    units: Optional[str] = None


@dataclass
class Alarm:
    """An alarm on a device channel."""

    enabled: Optional[bool] = None
    alarming: Optional[bool] = None
    value: Optional[int] = None
    """"The temperature units as a string like "F" """
    units: Optional[str] = None


@dataclass
class MinMaxReading:
    """A minimum or maximum reading on a device channel."""

    reading: Optional[Reading] = None
    date_reading: Optional[datetime] = None


@dataclass
class DeviceChannel:  # pylint: disable=too-many-instance-attributes
    """A device channel on a device.

    All fields are optional as different device types may have different properties.
    """

    last_telemetry_saved: Optional[datetime] = None
    """"The last time a telemetry packet was received from the device channel."""
    value: Optional[float] = None
    """"The temperature units as a string like "F" """
    units: Optional[str] = None
    """"The only observed value for this field is "NORMAL"."""
    status: Optional[str] = None
    type: Optional[str] = None
    """Customer provided 'name' for this device channel."""
    label: Optional[str] = None
    last_seen: Optional[datetime] = None
    alarm_high: Optional[Alarm] = None
    alarm_low: Optional[Alarm] = None
    """The device channel number"""
    number: Optional[str] = None
    minimum: Optional[MinMaxReading] = None
    maximum: Optional[MinMaxReading] = None
    show_avg_temp: Optional[bool] = None

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None


def _parse_alarm(alarm_data: dict) -> Alarm:
    """Parse alarm data into an Alarm object."""
    try:
        fields = alarm_data.get("fields", {})
        return Alarm(
            enabled=fields.get("enabled", {}).get("booleanValue"),
            alarming=fields.get("alarming", {}).get("booleanValue"),
            value=int(fields.get("value", {}).get("integerValue", 0)
                      ) if "value" in fields else None,
            units=fields.get("units", {}).get("stringValue"),
        )
    except (KeyError, TypeError, ValueError):
        return Alarm()


def _parse_min_max_reading(data: dict) -> MinMaxReading:
    """Parse minimum or maximum reading data."""
    try:
        fields = data.get("fields", {})
        reading_map = fields.get("reading", {}).get(
            "mapValue", {}).get("fields", {})

        reading = Reading(
            value=unwrap_firestore_value(reading_map.get(
                "value", {})) if "value" in reading_map else None,
            units=unwrap_firestore_value(reading_map.get(
                "units", {})) if "units" in reading_map else None,
        )

        date_reading = None
        if "dateReading" in fields and "timestampValue" in fields["dateReading"]:
            date_reading = parse_datetime(
                fields["dateReading"]["timestampValue"])

        return MinMaxReading(
            reading=reading,
            date_reading=date_reading,
        )
    except (KeyError, TypeError, ValueError):
        return MinMaxReading()


def _document_to_device_channel(document: dict) -> DeviceChannel:
    """Convert a Firestore Document object into a Device object."""
    fields = document.get("fields", {})
    device_channel = DeviceChannel()

    # Dictionary to store additional properties not explicitly defined
    additional_props = {}

    # Set standard properties if they exist
    try:
        if "lastTelemetrySaved" in fields and "timestampValue" in fields["lastTelemetrySaved"]:
            device_channel.last_telemetry_saved = parse_datetime(
                fields["lastTelemetrySaved"]["timestampValue"])

        device_channel.value = unwrap_firestore_value(
            fields.get("value", {})) if "value" in fields else None
        device_channel.units = get_field_value(fields, "units", "stringValue")
        device_channel.status = get_field_value(fields, "status", "stringValue")
        device_channel.type = get_field_value(fields, "type", "stringValue")
        device_channel.label = get_field_value(fields, "label", "stringValue")

        if "lastSeen" in fields and "timestampValue" in fields["lastSeen"]:
            device_channel.last_seen = parse_datetime(
                fields["lastSeen"]["timestampValue"])

        # Handle complex objects
        if "alarmHigh" in fields and "mapValue" in fields["alarmHigh"]:
            device_channel.alarm_high = _parse_alarm(
                fields["alarmHigh"]["mapValue"])

        if "alarmLow" in fields and "mapValue" in fields["alarmLow"]:
            device_channel.alarm_low = _parse_alarm(
                fields["alarmLow"]["mapValue"])

        device_channel.number = get_field_value(fields, "number", "stringValue")

        if "minimum" in fields and "mapValue" in fields["minimum"]:
            device_channel.minimum = _parse_min_max_reading(
                fields["minimum"]["mapValue"])

        if "maximum" in fields and "mapValue" in fields["maximum"]:
            device_channel.maximum = _parse_min_max_reading(
                fields["maximum"]["mapValue"])

        if "showAvgTemp" in fields and "booleanValue" in fields["showAvgTemp"]:
            device_channel.show_avg_temp = fields["showAvgTemp"]["booleanValue"]

        # Collect any additional fields not explicitly mapped
        known_fields = {
            "lastTelemetrySaved", "value", "units", "status", "type", "label",
            "lastSeen", "alarmHigh", "alarmLow", "number", "minimum", "maximum",
            "showAvgTemp"
        }

        for field_name, field_value in fields.items():
            if field_name not in known_fields:
                # Store the raw value for additional properties
                value_type = next(iter(field_value.keys()))
                additional_props[field_name] = field_value[value_type]

        if additional_props:
            device_channel.additional_properties = additional_props

    except (KeyError, TypeError, ValueError) as _:
        # If there's an error parsing a specific field, continue with what we have
        pass

    return device_channel