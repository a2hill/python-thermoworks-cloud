"""Classes related to a DeviceChannel."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict

from thermoworks_cloud.utils import parse_datetime, map_firestore_fields, parse_nested_object


@dataclass
class Reading:
    """A temperature reading from a device channel."""

    value: Optional[float] = field(default=None, metadata={
                                   "firestore_type": "doubleValue"})
    """"The temperature units as a string like "F" """
    units: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})


@dataclass
class Alarm:
    """An alarm on a device channel."""

    enabled: Optional[bool] = field(
        default=None, metadata={"firestore_type": "booleanValue"})
    alarming: Optional[bool] = field(
        default=None, metadata={"firestore_type": "booleanValue"})
    value: Optional[int] = field(default=None, metadata={
                                 "firestore_type": "integerValue", "converter": int})
    """"The temperature units as a string like "F" """
    units: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})


@dataclass
class MinMaxReading:
    """A minimum or maximum reading on a device channel."""

    reading: Optional[Reading] = None
    date_reading: Optional[datetime] = field(
        default=None,
        metadata={
            "firestore_type": "timestampValue",
            "converter": parse_datetime
        }
    )


@dataclass
class DeviceChannel:  # pylint: disable=too-many-instance-attributes
    """A device channel on a device.

    All fields are optional as different device types may have different properties.
    """

    last_telemetry_saved: Optional[datetime] = field(
        default=None,
        metadata={
            "firestore_type": "timestampValue",
            "converter": parse_datetime
        }
    )
    """"The last time a telemetry packet was received from the device channel."""
    value: Optional[float] = field(default=None, metadata={
                                   "firestore_type": "doubleValue"})
    """"The temperature units as a string like "F" """
    units: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})
    """"The only observed value for this field is "NORMAL"."""
    status: Optional[str] = field(default=None, metadata={
                                  "firestore_type": "stringValue"})
    type: Optional[str] = field(default=None, metadata={
                                "firestore_type": "stringValue"})
    """Customer provided 'name' for this device channel."""
    label: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})
    last_seen: Optional[datetime] = field(
        default=None,
        metadata={
            "firestore_type": "timestampValue",
            "converter": parse_datetime
        }
    )
    alarm_high: Optional[Alarm] = field(
        default=None, metadata={"api_name": "alarmHigh"})
    alarm_low: Optional[Alarm] = field(
        default=None, metadata={"api_name": "alarmLow"})
    """The device channel number"""
    number: Optional[str] = field(default=None, metadata={
                                  "firestore_type": "stringValue"})
    minimum: Optional[MinMaxReading] = None
    maximum: Optional[MinMaxReading] = None
    show_avg_temp: Optional[bool] = field(
        default=None,
        metadata={
            "api_name": "showAvgTemp",
            "firestore_type": "booleanValue"
        }
    )

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None


def _parse_min_max_reading(data: dict) -> Optional[MinMaxReading]:
    """Parse minimum or maximum reading data."""
    if not data or "fields" not in data:
        return None

    fields = data["fields"]
    result = MinMaxReading()

    # Parse date_reading
    if "dateReading" in fields and "timestampValue" in fields["dateReading"]:
        result.date_reading = parse_datetime(
            fields["dateReading"]["timestampValue"])

    # Parse reading
    if "reading" in fields and "mapValue" in fields["reading"]:
        result.reading = parse_nested_object(
            fields["reading"]["mapValue"], Reading)

    return result


def _document_to_device_channel(document: dict) -> DeviceChannel:
    """Convert a Firestore Document object into a Device object."""
    fields = document.get("fields", {})
    device_channel = map_firestore_fields(fields, DeviceChannel)

    try:
        # Handle complex objects
        if "alarmHigh" in fields and "mapValue" in fields["alarmHigh"]:
            device_channel.alarm_high = parse_nested_object(
                fields["alarmHigh"]["mapValue"], Alarm)

        if "alarmLow" in fields and "mapValue" in fields["alarmLow"]:
            device_channel.alarm_low = parse_nested_object(
                fields["alarmLow"]["mapValue"], Alarm)

        if "minimum" in fields and "mapValue" in fields["minimum"]:
            device_channel.minimum = _parse_min_max_reading(
                fields["minimum"]["mapValue"])

        if "maximum" in fields and "mapValue" in fields["maximum"]:
            device_channel.maximum = _parse_min_max_reading(
                fields["maximum"]["mapValue"])

    except (KeyError, TypeError, ValueError) as _:
        # If there's an error parsing a specific field, continue with what we have
        pass

    return device_channel
