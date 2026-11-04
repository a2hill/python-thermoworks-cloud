"""Classes related to a Device."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar, List, Optional, Dict, TypedDict

from thermoworks_cloud.utils import (
    parse_datetime,
    parse_optional_datetime,
    map_firestore_fields,
    parse_nested_object,
)

from .device_channel import DeviceChannel, DeviceChannelResponse, _json_to_device_channel


class _FanResponse(TypedDict, total=False):
    """A fan in a response from the ThermoWorks API. This is not in the API documentation."""

    connected: bool
    channel: Optional[str]
    setTemp: Optional[int]
    state: Optional[int]


class DeviceResponse(TypedDict, total=False):
    """A device in a response from the ThermoWorks API.

    `displayUnits`, `batteryState` and `fan` are not in the API documentation.
    """

    id: str
    serial: Optional[str]
    label: Optional[str]
    model: Optional[str]
    displayUnits: Optional[str]
    type: Optional[str]
    firmware: Optional[str]
    locationId: Optional[str]
    battery: Optional[float]
    batteryState: Optional[str]
    fan: Optional[_FanResponse]
    wifiSignal: Optional[float]
    gatewaySignal: Optional[float]
    lastSeen: Optional[str]
    nextExpectedConnection: Optional[str]
    transmitIntervalSeconds: Optional[float]
    channels: List[DeviceChannelResponse]


class DevicesResponse(TypedDict):
    """A response from the `/v1/devices` API."""

    generatedAt: str
    devices: List[DeviceResponse]


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

    Deprecated: these fields only exist in Firebase and `ThermoworksClient` leaves them unset.
    Delete them along with `core.py` once the EU API is live, see the documentation there:
    `color`, `thumbnail`, `iot_device_id`, `account_id`, `status`, `big_query_info`,
    `recording_interval_in_seconds`, `pending_load`, `battery_alert_sent`, `export_version`,
    `last_purged`, `last_archive`, `last_telemetry_saved`, `last_wifi_connection`,
    `last_bluetooth_connection`, `session_start`, `create_time` and `update_time`.
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
    battery: Optional[float] = field(
        default=None,
        metadata={
            "firestore_type": "integerValue",
            "converter": int
        }
    )
    wifi_strength: Optional[float] = field(
        default=None,
        metadata={
            "api_name": "wifi_stength",
            "firestore_type": "integerValue", "converter": int
        }
    )
    gateway_rssi: Optional[float] = field(
        default=None,
        metadata={
            "api_name": "gatewayRSSI",
            "firestore_type": ["integerValue", "stringValue"],
            "converter": int,
        }
    )
    recording_interval_in_seconds: Optional[int] = field(
        default=None, metadata={"firestore_type": "integerValue", "converter": int})
    transmit_interval_in_seconds: Optional[float] = field(
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

    # Only set by `ThermoworksClient`, which receives channels nested in each device.
    # Firebase channels are fetched separately with `ThermoworksCloud.get_device_channel`.
    channels: Optional[List[DeviceChannel]] = None

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None

    @property
    def signal_strength(self) -> Optional[float]:
        """Return the signal of the device's own connection, in dBm.

        Devices that report through an RFX gateway have `gateway_rssi`, while devices connected
        directly over Wi-Fi only have `wifi_strength`.
        """
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


def _json_to_fan(data: _FanResponse) -> Fan:
    """Convert a fan from the ThermoWorks API into a Fan object.

    The API documentation does not cover `fan`. RFX captures with Billows disconnected,
    paused, blowing and pulsing confirm these fields in ha-thermoworks-cloud issue #46:
    https://github.com/a2hill/ha-thermoworks-cloud/issues/46#issuecomment-6633438207
    A disconnected fan still reports its channel, setpoint and state; retain them as reported.
    Unlike Firebase, the API has no separate `connection` field.
    """
    known_fields = {"connected", "channel", "setTemp", "state"}
    additional_properties = {
        key: value for key, value in data.items() if key not in known_fields
    }
    fan_channel = data.get("channel")

    return Fan(
        connected=data.get("connected"),
        connection=data.get("connected"),
        fan_channel=str(fan_channel) if fan_channel is not None else None,
        set_temp=data.get("setTemp"),
        state=data.get("state"),
        additional_properties=additional_properties or None,
    )


def _json_to_device(data: DeviceResponse) -> Device:
    """Convert a device from the ThermoWorks API into a Device object.

    Most fields keep their Firebase meaning under a new name:
    - `id` is `device_id`. The API documentation makes it the authoritative identifier, since it
      is required and `serial` can be null. On the one Node captured so far, both match the
      Firebase values.
    - `model` is `device_name`, and `type` is unchanged. On that Node they are "node" and
      "datalogger" in both.
    - `wifiSignal` is `wifi_strength`, and `gatewaySignal` is `gateway_rssi`.

    `locationId` and `nextExpectedConnection` have no Firebase equivalent, so they are kept in
    `additional_properties`.

    `displayUnits`, `batteryState` and `fan` are returned by the service but are not in the API
    documentation, so they could change without notice.
    """
    known_fields = {
        "id",
        "serial",
        "label",
        "model",
        "displayUnits",
        "type",
        "firmware",
        "battery",
        "batteryState",
        "fan",
        "wifiSignal",
        "gatewaySignal",
        "lastSeen",
        "transmitIntervalSeconds",
        "channels",
    }
    additional_properties = {
        key: value for key, value in data.items() if key not in known_fields
    }
    fan = data.get("fan")

    return Device(
        device_id=data.get("id"),
        serial=data.get("serial"),
        label=data.get("label"),
        device_name=data.get("model"),
        device_display_units=data.get("displayUnits"),
        type=data.get("type"),
        firmware=data.get("firmware"),
        battery=data.get("battery"),
        battery_state=data.get("batteryState"),
        fan=_json_to_fan(fan) if fan else None,
        wifi_strength=data.get("wifiSignal"),
        gateway_rssi=data.get("gatewaySignal"),
        last_seen=parse_optional_datetime(data.get("lastSeen")),
        transmit_interval_in_seconds=data.get("transmitIntervalSeconds"),
        channels=[_json_to_device_channel(channel) for channel in data.get("channels", [])],
        additional_properties=additional_properties or None,
    )
