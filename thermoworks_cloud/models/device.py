"""Classes related to a Device."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, Optional, Dict

from thermoworks_cloud.utils import parse_datetime, map_firestore_fields, parse_nested_object
from thermoworks_cloud.utils import _object, _field, _timestamp, _additional


@dataclass
class BigQueryInfo:
    """BigQueryInfo contains information about the BigQuery table for a device."""

    table_id: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    dataset_id: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})


@dataclass
class Fan:
    """Fan contains information about a fan accessory connected to a device."""

    STATE_NAMES: ClassVar[Dict[int, str]] = {
        0: "Paused",
        1: "Blowing",
        2: "Pulsing",
    }

    connected: Optional[bool] = field(
        default=None, metadata={"firestore_type": "booleanValue"})
    connection: Optional[bool] = field(
        default=None, metadata={"firestore_type": "booleanValue"})
    fan_channel: Optional[str] = field(
        default=None,
        metadata={"api_name": "fan_channel", "firestore_type": "stringValue"},
    )
    set_temp: Optional[int] = field(
        default=None,
        metadata={
            "api_name": "setTemp",
            "firestore_type": "integerValue",
            "converter": int,
        },
    )
    state: Optional[int] = field(
        default=None, metadata={"firestore_type": "integerValue", "converter": int})

    additional_properties: Optional[Dict] = None

    @property
    def state_name(self) -> Optional[str]:
        """Return the ThermoWorks app name for the current fan state."""
        if self.state is None:
            return None
        return self.STATE_NAMES.get(self.state)


@dataclass
class Device:  # pylint: disable=too-many-instance-attributes
    """Device contains information about a Thermoworks device.

    All fields are optional as different device types may have different properties.
    The Node device type is known to have all these properties.
    """

    device_id: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    serial: Optional[str] = field(default=None, metadata={
                                  "firestore_type": "stringValue"})
    label: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})
    type: Optional[str] = field(default=None, metadata={
                                "firestore_type": "stringValue"})
    firmware: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    color: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})
    thumbnail: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    device_display_units: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    iot_device_id: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    device_name: Optional[str] = field(
        default=None, metadata={"api_name": "device", "firestore_type": "stringValue"})
    account_id: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    status: Optional[str] = field(default=None, metadata={
                                  "firestore_type": "stringValue"})
    battery_state: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    big_query_info: Optional[BigQueryInfo] = field(
        default=None, metadata={"api_name": "bigQuery"})
    fan: Optional[Fan] = None
    battery: Optional[int] = field(
        default=None,
        metadata={
            "firestore_type": "integerValue",
            "converter": int
        }
    )
    wifi_strength: Optional[int] = field(
        default=None,
        metadata={
            "api_name": "wifi_stength",
            "firestore_type": "integerValue", "converter": int
        }
    )
    gateway_rssi: Optional[int] = field(
        default=None,
        metadata={
            "api_name": "gatewayRSSI",
            "firestore_type": ["integerValue", "stringValue"],
            "converter": int,
        }
    )
    recording_interval_in_seconds: Optional[int] = field(
        default=None, metadata={"firestore_type": "integerValue", "converter": int})
    transmit_interval_in_seconds: Optional[int] = field(
        default=None, metadata={"firestore_type": "integerValue", "converter": int})
    pending_load: Optional[bool] = field(
        default=None, metadata={"firestore_type": "booleanValue"})
    battery_alert_sent: Optional[bool] = field(
        default=None, metadata={"firestore_type": "booleanValue"})
    export_version: Optional[float] = field(
        default=None, metadata={"firestore_type": "doubleValue"})
    last_seen: Optional[datetime] = field(
        default=None,
        metadata={"firestore_type": "timestampValue", "converter": parse_datetime})
    last_purged: Optional[datetime] = field(
        default=None,
        metadata={"firestore_type": "timestampValue", "converter": parse_datetime})
    last_archive: Optional[datetime] = field(
        default=None,
        metadata={"firestore_type": "timestampValue", "converter": parse_datetime})
    last_telemetry_saved: Optional[datetime] = field(
        default=None,
        metadata={"firestore_type": "timestampValue", "converter": parse_datetime})
    last_wifi_connection: Optional[datetime] = field(
        default=None,
        metadata={"firestore_type": "timestampValue", "converter": parse_datetime})
    last_bluetooth_connection: Optional[datetime] = field(
        default=None,
        metadata={"firestore_type": "timestampValue", "converter": parse_datetime})
    session_start: Optional[datetime] = field(
        default=None,
        metadata={"firestore_type": "timestampValue", "converter": parse_datetime})
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None

    @property
    def signal_strength(self) -> Optional[int]:
        """Return gateway RSSI when present, otherwise Wi-Fi strength, in dBm."""
        return self.gateway_rssi if self.gateway_rssi is not None else self.wifi_strength


def _document_to_device(document: dict) -> Device:
    """Convert a Firestore Document object into a Device object."""
    fields = document["fields"]
    device = map_firestore_fields(fields, Device)

    # Handle BigQuery info separately since it's a nested object
    if "bigQuery" in fields and "mapValue" in fields["bigQuery"]:
        try:
            device.big_query_info = parse_nested_object(
                fields["bigQuery"]["mapValue"], BigQueryInfo)
        except (KeyError, TypeError):
            device.big_query_info = None

    if "fan" in fields and "mapValue" in fields["fan"]:
        try:
            device.fan = parse_nested_object(fields["fan"]["mapValue"], Fan)
        except (KeyError, TypeError, ValueError):
            device.fan = None

    # Document timestamps
    if "createTime" in document:
        device.create_time = parse_datetime(document["createTime"])
    if "updateTime" in document:
        device.update_time = parse_datetime(document["updateTime"])

    return device


def _api_to_device(payload: dict) -> Device:
    """Map documented API fields to the existing device abstraction.

    API id is required and authoritative; a serial cannot replace it. Model
    and type are distinct. Firebase-only properties remain unset rather than
    being inferred, and unrecognized API fields remain in additional_properties.
    Channels belong to the response envelope and are converted separately.
    """
    data = _object(payload)
    device = Device(
        device_id=_field(data, "id", str, required=True),
        serial=_field(data, "serial", str),
        label=_field(data, "label", str),
        type=_field(data, "type", str),
        device_name=_field(data, "model", str),
        firmware=_field(data, "firmware", str),
        battery=_field(data, "battery", (int, float)),
        wifi_strength=_field(data, "wifiSignal", (int, float)),
        gateway_rssi=_field(data, "gatewaySignal", (int, float)),
        last_seen=_timestamp(data, "lastSeen"),
        transmit_interval_in_seconds=_field(data, "transmitIntervalSeconds", (int, float)),
    )
    device.additional_properties = _additional(data, {
        "id", "serial", "label", "type", "model", "firmware", "battery",
        "wifiSignal", "gatewaySignal", "lastSeen", "transmitIntervalSeconds", "channels",
    })
    return device
