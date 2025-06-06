"""Classes related to a Device."""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, Dict

from thermoworks_cloud.utils import parse_datetime, map_firestore_fields, parse_nested_object


@dataclass
class BigQueryInfo:
    """BigQueryInfo contains information about the BigQuery table for a device."""

    table_id: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    dataset_id: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})


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

    # Document timestamps
    if "createTime" in document:
        device.create_time = parse_datetime(document["createTime"])
    if "updateTime" in document:
        device.update_time = parse_datetime(document["updateTime"])

    return device
