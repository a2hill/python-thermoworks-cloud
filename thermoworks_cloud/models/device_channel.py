"""Classes related to a DeviceChannel."""

from dataclasses import dataclass
from datetime import datetime

from thermoworks_cloud.utils import parse_datetime


@dataclass
class Reading:
    """A temperature reading from a device channel."""

    value: float
    """"The temperature units as a string like "F" """
    units: str


@dataclass
class Alarm:
    """An alarm on a device channel."""

    enabled: bool
    alarming: bool
    value: int
    """"The temperature units as a string like "F" """
    units: str


@dataclass
class MinMaxReading:
    """A minimum or maximum reading on a device channel."""

    reading: Reading
    date_reading: datetime


@dataclass
class DeviceChannel:  # pylint: disable=too-many-instance-attributes
    """A device channel on a device."""

    last_telemetry_saved: datetime
    """"The last time a telemetry packet was received from the device channel."""
    value: float
    """"The temperature units as a string like "F" """
    units: str
    """"The only observed value for this field is "NORMAL"."""
    status: str
    type: str
    """Customer provided 'name' for this device channel."""
    label: str
    last_seen: datetime
    alarm_high: Alarm | None
    alarm_low: Alarm | None
    """The device channel number"""
    number: str
    minimum: MinMaxReading | None
    maximum: MinMaxReading | None
    show_avg_temp: bool


def _parse_alarm(alarm_data: dict) -> Alarm:
    """Parse alarm data into an Alarm object."""
    return Alarm(
        enabled=alarm_data["fields"]["enabled"]["booleanValue"],
        alarming=alarm_data["fields"]["alarming"]["booleanValue"],
        value=int(alarm_data["fields"]["value"]["integerValue"]),
        units=alarm_data["fields"]["units"]["stringValue"],
    )


def _parse_min_max_reading(data: dict) -> MinMaxReading:
    """Parse minimum or maximum reading data."""
    return MinMaxReading(
        reading=Reading(
            value=data["fields"]["reading"]["mapValue"]["fields"]["value"][
                "doubleValue"
            ],
            units=data["fields"]["reading"]["mapValue"]["fields"]["units"][
                "stringValue"
            ],
        ),
        date_reading=parse_datetime(
            data["fields"]["dateReading"]["timestampValue"]),
    )


def _document_to_device_channel(document: dict) -> DeviceChannel:
    """Convert a Firestore Document object into a Device object."""
    fields = document["fields"]

    return DeviceChannel(
        last_telemetry_saved=parse_datetime(
            fields["lastTelemetrySaved"]["timestampValue"]
        ),
        value=fields["value"]["doubleValue"],
        units=fields["units"]["stringValue"],
        status=fields["status"]["stringValue"],
        type=fields["type"]["stringValue"],
        label=fields["label"]["stringValue"],
        last_seen=parse_datetime(fields["lastSeen"]["timestampValue"]),
        alarm_high=(
            _parse_alarm(fields["alarmHigh"]["mapValue"])
            if "alarmHigh" in fields
            else None
        ),
        alarm_low=(
            _parse_alarm(fields["alarmLow"]["mapValue"])
            if "alarmLow" in fields
            else None
        ),
        number=fields["number"]["stringValue"],
        minimum=(
            _parse_min_max_reading(fields["minimum"]["mapValue"])
            if "minimum" in fields
            else None
        ),
        maximum=(
            _parse_min_max_reading(fields["maximum"]["mapValue"])
            if "maximum" in fields
            else None
        ),
        show_avg_temp=fields["showAvgTemp"]["booleanValue"],
    )
