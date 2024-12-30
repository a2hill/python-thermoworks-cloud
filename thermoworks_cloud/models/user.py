"""Classes related to User data"""

from dataclasses import dataclass
from datetime import datetime

from thermoworks_cloud.utils import parse_datetime


@dataclass
class EmailLastEvent:  # pylint: disable=too-many-instance-attributes
    """Contains information about the last email sent to a user."""

    reason: str
    event: str
    email: str
    bounce_classification: str
    tls: int
    timestamp: int
    smtp_id: str
    type: str
    sg_message_id: str
    sg_event_id: str


@dataclass
class DeviceOrderItem:
    """Contains information about a device's order within the users account."""

    device_id: str
    order: int


@dataclass
class User:  # pylint: disable=too-many-instance-attributes
    """Contains information about a User."""

    uid: str
    account_id: str
    display_name: str
    email: str
    provider: str
    time_zone: str
    app_version: str
    email_status: str
    preferred_units: str
    locale: str
    photo_url: str
    use_24_time: bool
    roles: dict[str, bool]
    account_roles: dict[str, bool]
    system: dict[str, bool]
    notification_settings: dict[str, bool]
    fcm_tokens: dict[str, bool]
    device_order: dict[str, list[DeviceOrderItem]]
    email_last_event: EmailLastEvent | None
    export_version: float
    last_seen_in_app: None
    last_login: datetime
    create_time: datetime
    update_time: datetime


def parse_email_last_event(data: dict) -> EmailLastEvent:
    """Parse emailLastEvent into an EmailLastEvent dataclass."""
    fields = data["fields"]
    return EmailLastEvent(
        reason=fields["reason"]["stringValue"],
        event=fields["event"]["stringValue"],
        email=fields["email"]["stringValue"],
        bounce_classification=fields["bounce_classification"]["stringValue"],
        tls=int(fields["tls"]["integerValue"]),
        timestamp=int(fields["timestamp"]["integerValue"]),
        smtp_id=fields["smtp-id"]["stringValue"],
        type=fields["type"]["stringValue"],
        sg_message_id=fields["sg_message_id"]["stringValue"],
        sg_event_id=fields["sg_event_id"]["stringValue"],
    )


def parse_device_order(data: dict) -> dict[str, list[DeviceOrderItem]]:
    """Parse deviceOrder into a dictionary of account ID to DeviceOrderItem list."""
    orders = {}
    for account_id, devices in data["fields"].items():
        orders[account_id] = [
            DeviceOrderItem(
                device_id=device["mapValue"]["fields"]["deviceId"]["stringValue"],
                order=int(device["mapValue"]["fields"]
                          ["order"]["integerValue"]),
            )
            for device in devices["arrayValue"]["values"]
        ]
    return orders


def document_to_user(document: dict) -> User:
    """Convert a Firestore Document object into a User object."""
    fields = document["fields"]

    return User(
        uid=fields["uid"]["stringValue"],
        account_id=fields["accountId"]["stringValue"],
        display_name=fields["displayName"]["stringValue"],
        email=fields["email"]["stringValue"],
        provider=fields["provider"]["stringValue"],
        time_zone=fields["timeZone"]["stringValue"],
        app_version=fields["appVersion"]["stringValue"],
        email_status=fields["emailStatus"]["stringValue"],
        preferred_units=fields["preferredUnits"]["stringValue"],
        locale=fields["locale"]["stringValue"],
        photo_url=fields["photoURL"]["stringValue"],
        use_24_time=fields["use24Time"]["booleanValue"],
        roles={
            k: v["booleanValue"]
            for k, v in fields["roles"]["mapValue"]["fields"].items()
        },
        account_roles={
            k: v["booleanValue"]
            for k, v in fields["accountRoles"]["mapValue"]["fields"].items()
        },
        system={
            k: v["booleanValue"]
            for k, v in fields["system"]["mapValue"]["fields"].items()
        },
        notification_settings={
            k: v["booleanValue"]
            for k, v in fields["notificationSettings"]["mapValue"]["fields"].items()
        },
        fcm_tokens={
            k: v["booleanValue"]
            for k, v in fields["fcmTokens"]["mapValue"]["fields"].items()
        },
        device_order=parse_device_order(fields["deviceOrder"]["mapValue"]),
        email_last_event=(
            parse_email_last_event(fields["emailLastEvent"]["mapValue"])
            if "emailLastEvent" in fields
            else None
        ),
        export_version=fields["exportVersion"]["doubleValue"],
        last_seen_in_app=None,  # Null field
        last_login=parse_datetime(fields["lastLogin"]["timestampValue"]),
        create_time=parse_datetime(document["createTime"]),
        update_time=parse_datetime(document["updateTime"]),
    )
