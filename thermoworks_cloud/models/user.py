"""Classes related to User data"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional, List

from thermoworks_cloud.utils import parse_datetime, map_firestore_fields, parse_nested_object


@dataclass
class EmailLastEvent:  # pylint: disable=too-many-instance-attributes
    """Contains information about the last email sent to a user."""

    reason: Optional[str] = field(default=None, metadata={
                                  "firestore_type": "stringValue"})
    event: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})
    email: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})
    bounce_classification: Optional[str] = field(
        default=None,
        metadata={
            "api_name": "bounce_classification",
            "firestore_type": "stringValue"
        }
    )
    tls: Optional[int] = field(default=None, metadata={
                               "firestore_type": "integerValue", "converter": int})
    timestamp: Optional[int] = field(
        default=None, metadata={"firestore_type": "integerValue", "converter": int})
    smtp_id: Optional[str] = field(
        default=None, metadata={"api_name": "smtp-id", "firestore_type": "stringValue"})
    type: Optional[str] = field(default=None, metadata={
                                "firestore_type": "stringValue"})
    sg_message_id: Optional[str] = field(
        default=None, metadata={"api_name": "sg_message_id", "firestore_type": "stringValue"})
    sg_event_id: Optional[str] = field(
        default=None, metadata={"api_name": "sg_event_id", "firestore_type": "stringValue"})

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None


@dataclass
class DeviceOrderItem:
    """Contains information about a device's order within the users account."""

    device_id: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    order: Optional[int] = field(default=None, metadata={
                                 "firestore_type": "integerValue", "converter": int})

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None


@dataclass
class User:  # pylint: disable=too-many-instance-attributes
    """Contains information about a User.

    All fields are optional as different users may have different properties.
    """

    uid: Optional[str] = field(default=None, metadata={
                               "firestore_type": "stringValue"})
    account_id: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    display_name: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    email: Optional[str] = field(default=None, metadata={
                                 "firestore_type": "stringValue"})
    provider: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    time_zone: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    app_version: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    preferred_units: Optional[str] = field(
        default=None, metadata={"firestore_type": "stringValue"})
    locale: Optional[str] = field(default=None, metadata={
                                  "firestore_type": "stringValue"})
    photo_url: Optional[str] = field(
        default=None, metadata={"api_name": "photoURL", "firestore_type": "stringValue"})
    use_24_time: Optional[bool] = field(
        default=None, metadata={"firestore_type": "booleanValue"})
    roles: Optional[Dict[str, bool]] = field(
        default=None, metadata={"map_of": "booleanValue"})
    account_roles: Optional[Dict[str, bool]] = field(
        default=None, metadata={"map_of": "booleanValue"})
    system: Optional[Dict[str, bool]] = field(
        default=None, metadata={"map_of": "booleanValue"})
    notification_settings: Optional[Dict[str, bool]] = field(
        default=None, metadata={"map_of": "booleanValue"})
    fcm_tokens: Optional[Dict[str, bool]] = field(
        default=None, metadata={"map_of": "booleanValue"})
    device_order: Optional[Dict[str, List[DeviceOrderItem]]] = None
    email_last_event: Optional[EmailLastEvent] = None
    export_version: Optional[float] = field(
        default=None, metadata={"firestore_type": "doubleValue"})
    last_seen_in_app: Optional[None] = field(
        default=None, metadata={"firestore_type": "nullValue"})
    last_login: Optional[datetime] = field(
        default=None,
        metadata={
            "firestore_type": "timestampValue",
            "converter": parse_datetime
        }
    )
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None


def parse_device_order(data: dict) -> Dict[str, List[DeviceOrderItem]]:
    """Parse deviceOrder into a dictionary of account ID to DeviceOrderItem list."""
    if not data or "fields" not in data:
        return {}

    orders = {}
    fields = data["fields"]

    for account_id, devices in fields.items():
        if "arrayValue" not in devices or "values" not in devices["arrayValue"]:
            continue

        device_items = []
        for device in devices["arrayValue"]["values"]:
            if "mapValue" not in device:
                continue

            item = parse_nested_object(device["mapValue"], DeviceOrderItem)
            if item:
                device_items.append(item)

        if device_items:
            orders[account_id] = device_items

    return orders


def document_to_user(document: dict) -> User:
    """Convert a Firestore Document object into a User object."""
    fields = document.get("fields", {})
    user = map_firestore_fields(fields, User)

    # Handle device order separately (complex nested structure)
    if "deviceOrder" in fields and "mapValue" in fields["deviceOrder"]:
        user.device_order = parse_device_order(
            fields["deviceOrder"]["mapValue"])

    # Handle email last event separately (nested object)
    if "emailLastEvent" in fields and "mapValue" in fields["emailLastEvent"]:
        user.email_last_event = parse_nested_object(
            fields["emailLastEvent"]["mapValue"], EmailLastEvent)

    # Document timestamps
    if "createTime" in document:
        user.create_time = parse_datetime(document["createTime"])
    if "updateTime" in document:
        user.update_time = parse_datetime(document["updateTime"])

    return user
