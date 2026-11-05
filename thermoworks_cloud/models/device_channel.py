"""Classes related to a DeviceChannel."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict, TypedDict

from thermoworks_cloud.utils import (
    parse_datetime,
    parse_optional_datetime,
    map_firestore_fields,
    parse_nested_object,
)


class _AlarmResponse(TypedDict, total=False):
    """An alarm in a response from the ThermoWorks API."""

    enabled: bool
    value: Optional[float]
    alarming: bool


class DeviceChannelResponse(TypedDict, total=False):
    """A channel in a response from the ThermoWorks API."""

    id: str
    number: Optional[int]
    label: Optional[str]
    type: Optional[str]
    enabled: bool
    value: Optional[float]
    units: Optional[str]
    status: Optional[str]
    probeFailed: bool
    alarming: bool
    alarmHigh: Optional[_AlarmResponse]
    alarmLow: Optional[_AlarmResponse]
    minimum: Optional[float]
    maximum: Optional[float]
    lastTelemetrySaved: Optional[str]
    lastSeen: Optional[str]


@dataclass
class Reading:
    """A reading from a device channel (temperature or humidity)."""

    value: Optional[float] = field(default=None, metadata={
                                   "firestore_type": "doubleValue"})
    """"The units as a string like "F", "C", or "H" (for humidity)"""
    units: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})


@dataclass
class Alarm:
    """An alarm on a device channel."""

    enabled: Optional[bool] = field(
        default=None, metadata={"firestore_type": "booleanValue"})
    alarming: Optional[bool] = field(
        default=None, metadata={"firestore_type": "booleanValue"})
    value: Optional[float] = field(default=None, metadata={
                                   "firestore_type": "integerValue", "converter": int})
    """"The units as a string like "F", "C", or "H" (for humidity)"""
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

    Deprecated: `show_avg_temp` and `MinMaxReading.date_reading` only exist in Firebase and
    `ThermoworksClient` leaves them unset. Delete them along with `core.py` once the EU API is
    live, see the documentation there.
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
                                   "firestore_type": ["doubleValue","integerValue"]})
    """"The units as a string like "F", "C", or "H" (for humidity)"""
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
                                  "firestore_type": ["stringValue", "integerValue"],
                                  "converter": str})
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


def _json_to_alarm(data: Optional[_AlarmResponse], units: Optional[str]) -> Optional[Alarm]:
    """Convert an alarm from the ThermoWorks API into an Alarm object.

    Unlike Firebase, API alarms have no units of their own. The channel converter supplies
    the appropriate units; temperature thresholds use the parent device's display units.
    """
    if not data:
        return None

    return Alarm(
        enabled=data.get("enabled"),
        alarming=data.get("alarming"),
        value=data.get("value"),
        units=units,
    )


def _json_to_min_max_reading(
    value: Optional[float], units: Optional[str]
) -> Optional[MinMaxReading]:
    """Convert a minimum or maximum from the ThermoWorks API into a MinMaxReading object.

    Unlike Firebase, the API only provides the value, so `date_reading` is left unset.
    """
    if value is None:
        return None

    return MinMaxReading(reading=Reading(value=value, units=units))


def _json_to_device_channel(
    data: DeviceChannelResponse, device_display_units: Optional[str]
) -> DeviceChannel:
    """Convert a channel from the ThermoWorks API into a DeviceChannel object.

    Firebase only has `number`. `id` has been observed to be the same number as a string, but it
    is kept in `additional_properties` along with the other API fields that have no Firebase
    equivalent: `enabled`, `alarming` and `probeFailed`.

    Temperature readings and extrema use channel units, but alarm thresholds use the device's
    display units. Leave temperature alarm units unknown when display units are unavailable.
    Keep the existing channel-unit behavior for non-temperature readings.
    """
    known_fields = {
        "number",
        "label",
        "type",
        "value",
        "units",
        "status",
        "alarmHigh",
        "alarmLow",
        "minimum",
        "maximum",
        "lastTelemetrySaved",
        "lastSeen",
    }
    additional_properties = {
        key: value for key, value in data.items() if key not in known_fields
    }
    number = data.get("number")
    units = data.get("units")
    alarm_units = device_display_units if units in ("F", "C") else units

    return DeviceChannel(
        number=str(number) if number is not None else None,
        label=data.get("label"),
        type=data.get("type"),
        value=data.get("value"),
        units=units,
        status=data.get("status"),
        alarm_high=_json_to_alarm(data.get("alarmHigh"), alarm_units),
        alarm_low=_json_to_alarm(data.get("alarmLow"), alarm_units),
        minimum=_json_to_min_max_reading(data.get("minimum"), units),
        maximum=_json_to_min_max_reading(data.get("maximum"), units),
        last_telemetry_saved=parse_optional_datetime(data.get("lastTelemetrySaved")),
        last_seen=parse_optional_datetime(data.get("lastSeen")),
        additional_properties=additional_properties or None,
    )
