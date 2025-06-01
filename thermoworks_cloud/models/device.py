"""Classes related to a Device."""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict

from thermoworks_cloud.utils import parse_datetime, get_field_value, extract_additional_properties


@dataclass
class BigQueryInfo:
    """BigQueryInfo contains information about the BigQuery table for a device."""

    table_id: Optional[str] = None
    dataset_id: Optional[str] = None


@dataclass
class Device:  # pylint: disable=too-many-instance-attributes
    """Device contains information about a Thermoworks device.

    All fields are optional as different device types may have different properties.
    The Node device type is known to have all these properties.
    """

    device_id: Optional[str] = None
    serial: Optional[str] = None
    label: Optional[str] = None
    type: Optional[str] = None
    firmware: Optional[str] = None
    color: Optional[str] = None
    thumbnail: Optional[str] = None
    device_display_units: Optional[str] = None
    iot_device_id: Optional[str] = None
    device_name: Optional[str] = None
    account_id: Optional[str] = None
    status: Optional[str] = None
    battery_state: Optional[str] = None
    big_query_info: Optional[BigQueryInfo] = None
    battery: Optional[int] = None
    wifi_strength: Optional[int] = None
    recording_interval_in_seconds: Optional[int] = None
    transmit_interval_in_seconds: Optional[int] = None
    pending_load: Optional[bool] = None
    battery_alert_sent: Optional[bool] = None
    export_version: Optional[float] = None
    last_seen: Optional[datetime] = None
    last_purged: Optional[datetime] = None
    last_archive: Optional[datetime] = None
    last_telemetry_saved: Optional[datetime] = None
    last_wifi_connection: Optional[datetime] = None
    last_bluetooth_connection: Optional[datetime] = None
    session_start: Optional[datetime] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None


def _parse_big_query_info(data: dict) -> Optional[BigQueryInfo]:
    """Parse bigQuery into a BigQueryInfo dataclass."""
    fields = data.get("fields", {})

    # Check if required fields exist
    if "tableId" not in fields or "datasetId" not in fields:
        return None

    try:
        return BigQueryInfo(
            table_id=fields["tableId"]["stringValue"],
            dataset_id=fields["datasetId"]["stringValue"],
        )
    except (KeyError, TypeError):
        return None


def _document_to_device(document: dict) -> Device:
    """Convert a Firestore Document object into a Device object."""
    fields = document["fields"]
    device = Device()

    # Set standard properties if they exist
    device.device_id = get_field_value(fields, "deviceId", "stringValue")
    device.serial = get_field_value(fields, "serial", "stringValue")
    device.label = get_field_value(fields, "label", "stringValue")
    device.type = get_field_value(fields, "type", "stringValue")
    device.firmware = get_field_value(fields, "firmware", "stringValue")
    device.color = get_field_value(fields, "color", "stringValue")
    device.thumbnail = get_field_value(fields, "thumbnail", "stringValue")
    device.device_display_units = get_field_value(
        fields, "deviceDisplayUnits", "stringValue")
    device.iot_device_id = get_field_value(
        fields, "iotDeviceId", "stringValue")
    device.device_name = get_field_value(fields, "device", "stringValue")
    device.account_id = get_field_value(fields, "accountId", "stringValue")
    device.status = get_field_value(fields, "status", "stringValue")
    device.battery_state = get_field_value(
        fields, "batteryState", "stringValue")

    # Handle BigQuery info
    if "bigQuery" in fields and "mapValue" in fields["bigQuery"]:
        try:
            device.big_query_info = _parse_big_query_info(
                fields["bigQuery"]["mapValue"])
        except (KeyError, TypeError):
            device.big_query_info = None

    # Handle numeric values
    device.battery = get_field_value(fields, "battery", "integerValue", int)
    device.wifi_strength = get_field_value(
        fields, "wifi_stength", "integerValue", int)
    device.recording_interval_in_seconds = get_field_value(
        fields, "recordingIntervalInSeconds", "integerValue", int)
    device.transmit_interval_in_seconds = get_field_value(
        fields, "transmitIntervalInSeconds", "integerValue", int)

    # Handle boolean values
    device.pending_load = get_field_value(
        fields, "pendingLoad", "booleanValue")
    device.battery_alert_sent = get_field_value(
        fields, "batteryAlertSent", "booleanValue")

    # Handle float values
    device.export_version = get_field_value(
        fields, "exportVersion", "doubleValue")

    # Handle datetime values
    device.last_seen = get_field_value(
        fields, "lastSeen", "timestampValue", parse_datetime)
    device.last_purged = get_field_value(
        fields, "lastPurged", "timestampValue", parse_datetime)
    device.last_archive = get_field_value(
        fields, "lastArchive", "timestampValue", parse_datetime)
    device.last_telemetry_saved = get_field_value(
        fields, "lastTelemetrySaved", "timestampValue", parse_datetime)
    device.last_wifi_connection = get_field_value(
        fields, "lastWifiConnection", "timestampValue", parse_datetime)
    device.last_bluetooth_connection = get_field_value(
        fields, "lastBluetoothConnection", "timestampValue", parse_datetime)
    device.session_start = get_field_value(
        fields, "sessionStart", "timestampValue", parse_datetime)

    # Document timestamps
    if "createTime" in document:
        device.create_time = parse_datetime(document["createTime"])
    if "updateTime" in document:
        device.update_time = parse_datetime(document["updateTime"])

    # Extract additional properties
    device.additional_properties = extract_additional_properties(
        fields,
        {
            "deviceId", "serial", "label", "type", "firmware", "color", "thumbnail",
            "deviceDisplayUnits", "iotDeviceId", "device", "accountId", "status",
            "batteryState", "bigQuery", "battery", "wifi_stength", "recordingIntervalInSeconds",
            "transmitIntervalInSeconds", "pendingLoad", "batteryAlertSent", "exportVersion",
            "lastSeen", "lastPurged", "lastArchive", "lastTelemetrySaved", "lastWifiConnection",
            "lastBluetoothConnection", "sessionStart"
        }
    )

    return device
