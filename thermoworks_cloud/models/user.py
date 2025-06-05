"""Classes related to User data"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Optional

from thermoworks_cloud.utils import parse_datetime, get_field_value, extract_additional_properties


@dataclass
class EmailLastEvent:  # pylint: disable=too-many-instance-attributes
    """Contains information about the last email sent to a user."""

    reason: Optional[str] = None
    event: Optional[str] = None
    email: Optional[str] = None
    bounce_classification: Optional[str] = field(
        # Keeps underscores
        default=None, metadata={"api_name": "bounce_classification"})
    tls: Optional[int] = None
    timestamp: Optional[int] = None
    smtp_id: Optional[str] = field(
        default=None, metadata={"api_name": "smtp-id"})  # Uses hyphen
    type: Optional[str] = None
    sg_message_id: Optional[str] = field(
        # Keeps underscores
        default=None, metadata={"api_name": "sg_message_id"})
    sg_event_id: Optional[str] = field(
        # Keeps underscores
        default=None, metadata={"api_name": "sg_event_id"})

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None


@dataclass
class DeviceOrderItem:
    """Contains information about a device's order within the users account."""

    device_id: Optional[str] = None
    order: Optional[int] = None

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None


@dataclass
class User:  # pylint: disable=too-many-instance-attributes
    """Contains information about a User.

    All fields are optional as different users may have different properties.
    """

    uid: Optional[str] = None
    account_id: Optional[str] = None
    display_name: Optional[str] = None
    email: Optional[str] = None
    provider: Optional[str] = None
    time_zone: Optional[str] = None
    app_version: Optional[str] = None
    preferred_units: Optional[str] = None
    locale: Optional[str] = None
    photo_url: Optional[str] = field(
        default=None, metadata={"api_name": "photoURL"})
    use_24_time: Optional[bool] = None
    roles: Optional[Dict[str, bool]] = None
    account_roles: Optional[Dict[str, bool]] = None
    system: Optional[Dict[str, bool]] = None
    notification_settings: Optional[Dict[str, bool]] = None
    fcm_tokens: Optional[Dict[str, bool]] = None
    device_order: Optional[Dict[str, list[DeviceOrderItem]]] = None
    email_last_event: Optional[EmailLastEvent] = None
    export_version: Optional[float] = None
    last_seen_in_app: Optional[None] = None
    last_login: Optional[datetime] = None
    create_time: Optional[datetime] = None
    update_time: Optional[datetime] = None

    # Dictionary to store any additional properties not explicitly defined
    additional_properties: Optional[Dict] = None


def parse_email_last_event(data: dict) -> EmailLastEvent:
    """Parse emailLastEvent into an EmailLastEvent dataclass."""
    fields = data.get("fields", {})
    event = EmailLastEvent()

    # Set standard properties if they exist
    event.reason = get_field_value(fields, "reason", "stringValue")
    event.event = get_field_value(fields, "event", "stringValue")
    event.email = get_field_value(fields, "email", "stringValue")
    event.bounce_classification = get_field_value(
        fields, "bounce_classification", "stringValue")
    event.tls = get_field_value(fields, "tls", "integerValue", int)
    event.timestamp = get_field_value(fields, "timestamp", "integerValue", int)
    event.smtp_id = get_field_value(fields, "smtp-id", "stringValue")
    event.type = get_field_value(fields, "type", "stringValue")
    event.sg_message_id = get_field_value(
        fields, "sg_message_id", "stringValue")
    event.sg_event_id = get_field_value(fields, "sg_event_id", "stringValue")

    # Extract additional properties
    event.additional_properties = extract_additional_properties(
        fields, EmailLastEvent)

    return event


def parse_device_order(data: dict) -> Dict[str, list[DeviceOrderItem]]:
    """Parse deviceOrder into a dictionary of account ID to DeviceOrderItem list."""
    orders = {}
    fields = data.get("fields", {})

    for account_id, devices in fields.items():
        if "arrayValue" not in devices or "values" not in devices["arrayValue"]:
            continue

        device_items = []
        for device in devices["arrayValue"]["values"]:
            if "mapValue" not in device or "fields" not in device["mapValue"]:
                continue

            device_fields = device["mapValue"]["fields"]
            item = DeviceOrderItem()

            # Set standard properties if they exist
            item.device_id = get_field_value(
                device_fields, "deviceId", "stringValue")
            item.order = get_field_value(
                device_fields, "order", "integerValue", int)

            # Extract additional properties
            item.additional_properties = extract_additional_properties(
                device_fields, DeviceOrderItem)

            device_items.append(item)

        if device_items:
            orders[account_id] = device_items

    return orders


def document_to_user(document: dict) -> User:
    """Convert a Firestore Document object into a User object."""
    fields = document.get("fields", {})
    user = User()

    # Set standard properties if they exist
    user.uid = get_field_value(fields, "uid", "stringValue")
    user.account_id = get_field_value(fields, "accountId", "stringValue")
    user.display_name = get_field_value(fields, "displayName", "stringValue")
    user.email = get_field_value(fields, "email", "stringValue")
    user.provider = get_field_value(fields, "provider", "stringValue")
    user.time_zone = get_field_value(fields, "timeZone", "stringValue")
    user.app_version = get_field_value(fields, "appVersion", "stringValue")
    user.preferred_units = get_field_value(
        fields, "preferredUnits", "stringValue")
    user.locale = get_field_value(fields, "locale", "stringValue")
    user.photo_url = get_field_value(fields, "photoURL", "stringValue")
    user.use_24_time = get_field_value(fields, "use24Time", "booleanValue")

    # Handle map values
    if "roles" in fields and "mapValue" in fields["roles"] and "fields" in fields["roles"]["mapValue"]:
        user.roles = {
            k: v.get("booleanValue", False)
            for k, v in fields["roles"]["mapValue"]["fields"].items()
        }

    if "accountRoles" in fields and "mapValue" in fields["accountRoles"] and "fields" in fields["accountRoles"]["mapValue"]:
        user.account_roles = {
            k: v.get("booleanValue", False)
            for k, v in fields["accountRoles"]["mapValue"]["fields"].items()
        }

    if "system" in fields and "mapValue" in fields["system"] and "fields" in fields["system"]["mapValue"]:
        user.system = {
            k: v.get("booleanValue", False)
            for k, v in fields["system"]["mapValue"]["fields"].items()
        }

    if "notificationSettings" in fields and "mapValue" in fields["notificationSettings"] and "fields" in fields["notificationSettings"]["mapValue"]:
        user.notification_settings = {
            k: v.get("booleanValue", False)
            for k, v in fields["notificationSettings"]["mapValue"]["fields"].items()
        }

    if "fcmTokens" in fields and "mapValue" in fields["fcmTokens"] and "fields" in fields["fcmTokens"]["mapValue"]:
        user.fcm_tokens = {
            k: v.get("booleanValue", False)
            for k, v in fields["fcmTokens"]["mapValue"]["fields"].items()
        }

    # Handle device order
    if "deviceOrder" in fields and "mapValue" in fields["deviceOrder"]:
        user.device_order = parse_device_order(
            fields["deviceOrder"]["mapValue"])

    # Handle email last event
    if "emailLastEvent" in fields and "mapValue" in fields["emailLastEvent"]:
        user.email_last_event = parse_email_last_event(
            fields["emailLastEvent"]["mapValue"])

    # Handle other fields
    user.export_version = get_field_value(
        fields, "exportVersion", "doubleValue")
    user.last_seen_in_app = None  # Null field

    if "lastLogin" in fields and "timestampValue" in fields["lastLogin"]:
        user.last_login = parse_datetime(fields["lastLogin"]["timestampValue"])

    # Document timestamps
    if "createTime" in document:
        user.create_time = parse_datetime(document["createTime"])
    if "updateTime" in document:
        user.update_time = parse_datetime(document["updateTime"])

    # Extract additional properties
    user.additional_properties = extract_additional_properties(fields, User)

    return user
