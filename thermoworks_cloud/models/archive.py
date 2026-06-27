"""Classes related to archived ThermoWorks device readings."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from thermoworks_cloud.utils import (
    get_field_value,
    map_firestore_fields,
    parse_datetime,
    unwrap_firestore_value,
)


@dataclass
class ArchiveMetadata:  # pylint: disable=too-many-instance-attributes
    """Metadata for a historical archive stored by ThermoWorks Cloud."""

    archive_id: Optional[str] = None
    """Identifier of the archive metadata document within a device's archive collection."""
    type: Optional[str] = field(default=None, metadata={"firestore_type": "stringValue"})
    """Archive type reported by ThermoWorks, such as ``auto`` or ``manual``."""
    label: Optional[str] = field(default=None, metadata={"firestore_type": "stringValue"})
    """Human-readable archive label."""
    notes: Optional[str] = field(default=None, metadata={"firestore_type": "stringValue"})
    """User notes associated with the archive."""
    filename: Optional[str] = field(default=None, metadata={"firestore_type": "stringValue"})
    """Firebase Storage object name used to retrieve the archive readings."""
    device_label: Optional[str] = field(
        default=None, metadata={"api_name": "deviceLabel", "firestore_type": "stringValue"}
    )
    """Device label at the time the archive was created."""
    public: Optional[bool] = field(default=None, metadata={"firestore_type": "booleanValue"})
    """Whether ThermoWorks marks the archive as publicly shared."""
    public_link: Optional[str] = field(
        default=None, metadata={"api_name": "publicLink", "firestore_type": "stringValue"}
    )
    """Public sharing link identifier when sharing is enabled."""
    count: Optional[int] = field(
        default=None, metadata={"firestore_type": "integerValue", "converter": int}
    )
    """Number of readings reported by the archive metadata document."""
    start: Optional[datetime] = field(
        default=None,
        metadata={"firestore_type": "timestampValue", "converter": parse_datetime},
    )
    """Start timestamp for the archived range."""
    end: Optional[datetime] = field(
        default=None,
        metadata={"firestore_type": "timestampValue", "converter": parse_datetime},
    )
    """End timestamp for the archived range."""
    created_on: Optional[datetime] = field(
        default=None,
        metadata={
            "api_name": "createdOn",
            "firestore_type": "timestampValue",
            "converter": parse_datetime,
        },
    )
    """Timestamp when ThermoWorks created the archive."""
    channels: Optional[List[Dict[str, Any]]] = None
    """Channel metadata included with the archive."""
    events: Optional[List[Dict[str, Any]]] = None
    """Event metadata included with the archive."""
    device_data: Optional[Dict[str, Any]] = None
    """Device metadata included with the archive."""

    additional_properties: Optional[Dict] = None
    """Unmodeled properties returned by ThermoWorks."""


@dataclass
class ArchiveReading:
    """A single reading from an archived ThermoWorks data file."""

    channel: str
    """Channel number associated with the reading."""
    timestamp: datetime
    """Timestamp of the reading."""
    value: float
    """Measured reading value."""
    units: str
    """Reading units, such as ``F``, ``C``, or ``H`` for humidity."""


@dataclass
class ArchiveData(ArchiveMetadata):
    """The parsed contents of an archived ThermoWorks data object."""

    readings: List[ArchiveReading] = field(default_factory=list)
    """Readings contained in the archive."""
    serial: Optional[str] = None
    """Device serial reported by the archive data object."""


def _document_to_archive_metadata(document: dict) -> ArchiveMetadata:
    """Convert a Firestore Document object into archive metadata."""
    fields = document.get("fields", {})
    archive = map_firestore_fields(fields, ArchiveMetadata)

    if "name" in document:
        archive.archive_id = document["name"].rsplit("/", 1)[-1]

    archive.channels = get_field_value(
        fields, "channels", "arrayValue", unwrap_firestore_value
    )
    archive.events = get_field_value(
        fields, "events", "arrayValue", unwrap_firestore_value
    )
    archive.device_data = get_field_value(
        fields, "deviceData", "mapValue", unwrap_firestore_value
    )

    return archive


def _archive_json_to_data(data: dict, filename: Optional[str] = None) -> ArchiveData:
    """Convert a downloaded ThermoWorks archive JSON object into archive data."""
    known_fields = {
        "serial",
        "type",
        "label",
        "notes",
        "deviceLabel",
        "start",
        "end",
        "channels",
        "events",
        "deviceData",
        "readings",
    }
    additional_properties = {
        key: value for key, value in data.items() if key not in known_fields
    }

    return ArchiveData(
        filename=filename,
        readings=[_archive_reading_from_row(row) for row in data.get("readings", [])],
        events=data.get("events", []),
        channels=data.get("channels", []),
        device_data=data.get("deviceData"),
        serial=data.get("serial"),
        type=data.get("type"),
        label=data.get("label"),
        notes=data.get("notes"),
        device_label=data.get("deviceLabel"),
        start=_parse_archive_datetime(data.get("start")),
        end=_parse_archive_datetime(data.get("end")),
        additional_properties=additional_properties or None,
    )


def _archive_reading_from_row(row: list) -> ArchiveReading:
    """Parse an archive reading row in the observed [channel, ts, value, unit] format."""
    if len(row) < 4:
        raise ValueError("Archive reading rows must contain channel, timestamp, value, and units")

    return ArchiveReading(
        channel=str(row[0]),
        timestamp=_parse_archive_datetime(row[1]),
        value=float(row[2]),
        units=str(row[3]),
    )


def _parse_archive_datetime(value: Any) -> Optional[datetime]:
    """Parse timestamps from archive JSON fields."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, (int, float)):
        timestamp = value / 1000 if value > 10_000_000_000 else value
        return datetime.fromtimestamp(timestamp, timezone.utc)
    return parse_datetime(str(value))
