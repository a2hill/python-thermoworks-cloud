"""Classes related to a Device."""

from dataclasses import dataclass
from datetime import datetime

from thermoworks_cloud.utils import parse_datetime


@dataclass
class BigQueryInfo:
    """BigQueryInfo contains information about the BigQuery table for a device."""

    table_id: str
    dataset_id: str


@dataclass
class Device:  # pylint: disable=too-many-instance-attributes
    """Device contains information about a Thermoworks device."""

    device_id: str
    serial: str
    label: str
    type: str
    firmware: str
    color: str
    thumbnail: str
    device_display_units: str
    iot_device_id: str
    device_name: str
    account_id: str
    status: str
    battery_state: str
    big_query_info: BigQueryInfo
    battery: int
    wifi_strength: int
    recording_interval_in_seconds: int
    transmit_interval_in_seconds: int
    pending_load: bool
    battery_alert_sent: bool
    export_version: float
    last_seen: datetime
    last_purged: datetime
    last_archive: datetime
    last_telemetry_saved: datetime
    last_wifi_connection: datetime
    last_bluetooth_connection: datetime
    session_start: datetime
    create_time: datetime
    update_time: datetime


def _parse_big_query_info(data: dict) -> BigQueryInfo:
    """Parse bigQuery into a BigQueryInfo dataclass."""
    fields = data["fields"]
    return BigQueryInfo(
        table_id=fields["tableId"]["stringValue"],
        dataset_id=fields["datasetId"]["stringValue"],
    )


def _document_to_device(document: dict) -> Device:
    """Convert a Firestore Document object into a Device object."""
    fields = document["fields"]

    return Device(
        device_id=fields["deviceId"]["stringValue"],
        serial=fields["serial"]["stringValue"],
        label=fields["label"]["stringValue"],
        type=fields["type"]["stringValue"],
        firmware=fields["firmware"]["stringValue"],
        color=fields["color"]["stringValue"],
        thumbnail=fields["thumbnail"]["stringValue"],
        device_display_units=fields["deviceDisplayUnits"]["stringValue"],
        iot_device_id=fields["iotDeviceId"]["stringValue"],
        device_name=fields["device"]["stringValue"],
        account_id=fields["accountId"]["stringValue"],
        status=fields["status"]["stringValue"],
        battery_state=fields["batteryState"]["stringValue"],
        big_query_info=_parse_big_query_info(fields["bigQuery"]["mapValue"]),
        battery=int(fields["battery"]["integerValue"]),
        wifi_strength=int(fields["wifi_stength"]["integerValue"]),
        recording_interval_in_seconds=int(
            fields["recordingIntervalInSeconds"]["integerValue"]
        ),
        transmit_interval_in_seconds=int(
            fields["transmitIntervalInSeconds"]["integerValue"]
        ),
        pending_load=fields["pendingLoad"]["booleanValue"],
        battery_alert_sent=fields["batteryAlertSent"]["booleanValue"],
        export_version=fields["exportVersion"]["doubleValue"],
        last_seen=parse_datetime(fields["lastSeen"]["timestampValue"]),
        last_purged=parse_datetime(fields["lastPurged"]["timestampValue"]),
        last_archive=parse_datetime(fields["lastArchive"]["timestampValue"]),
        last_telemetry_saved=parse_datetime(
            fields["lastTelemetrySaved"]["timestampValue"]
        ),
        last_wifi_connection=parse_datetime(
            fields["lastWifiConnection"]["timestampValue"]
        ),
        last_bluetooth_connection=parse_datetime(
            fields["lastBluetoothConnection"]["timestampValue"]
        ),
        session_start=parse_datetime(fields["sessionStart"]["timestampValue"]),
        create_time=parse_datetime(document["createTime"]),
        update_time=parse_datetime(document["updateTime"]),
    )
