"""Test suite for handling missing fields and additional properties."""

from copy import deepcopy

from thermoworks_cloud.models.device import _document_to_device
from thermoworks_cloud.models.device_channel import _document_to_device_channel
from thermoworks_cloud.models.user import document_to_user
from tests.test_data import (
    GET_DEVICE_RESPONSE,
    GET_DEVICE_CHANNEL_RESPONSE,
    USER_RESPONSE,
)


def test_user_missing_fields():
    """Test that the User model handles missing fields gracefully."""
    # Create a copy of the response with some fields removed
    modified_response = deepcopy(USER_RESPONSE)
    del modified_response["fields"]["displayName"]
    del modified_response["fields"]["photoURL"]
    del modified_response["fields"]["system"]

    # Parse the modified response
    user = document_to_user(modified_response)

    # Check that the missing fields are None
    assert user.display_name is None
    assert user.photo_url is None
    assert user.system is None

    # Check that other fields are still present
    assert user.uid is not None
    assert user.email is not None


def test_user_additional_properties():
    """Test that the User model handles additional properties correctly."""
    # Create a copy of the response with an additional field
    modified_response = deepcopy(USER_RESPONSE)
    modified_response["fields"]["newField"] = {"stringValue": "new value"}
    modified_response["fields"]["anotherNewField"] = {"integerValue": "42"}

    # Parse the modified response
    user = document_to_user(modified_response)

    # Check that the additional properties are stored
    assert user.additional_properties is not None
    assert "newField" in user.additional_properties
    assert user.additional_properties["newField"] == "new value"
    assert "anotherNewField" in user.additional_properties
    assert user.additional_properties["anotherNewField"] == "42"


def test_device_missing_fields():
    """Test that the Device model handles missing fields gracefully."""
    # Create a copy of the response with some fields removed
    modified_response = deepcopy(GET_DEVICE_RESPONSE)
    del modified_response["fields"]["label"]
    del modified_response["fields"]["color"]
    del modified_response["fields"]["bigQuery"]

    # Parse the modified response
    device = _document_to_device(modified_response)

    # Check that the missing fields are None
    assert device.label is None
    assert device.color is None
    assert device.big_query_info is None

    # Check that other fields are still present
    assert device.device_id is not None
    assert device.serial is not None


def test_device_additional_properties():
    """Test that the Device model handles additional properties correctly."""
    # Create a copy of the response with an additional field
    modified_response = deepcopy(GET_DEVICE_RESPONSE)
    modified_response["fields"]["newField"] = {"stringValue": "new value"}
    modified_response["fields"]["anotherNewField"] = {"integerValue": "42"}

    # Parse the modified response
    device = _document_to_device(modified_response)

    # Check that the additional properties are stored
    assert device.additional_properties is not None
    assert "newField" in device.additional_properties
    assert device.additional_properties["newField"] == "new value"
    assert "anotherNewField" in device.additional_properties
    assert device.additional_properties["anotherNewField"] == "42"


def test_device_channel_missing_fields():
    """Test that the DeviceChannel model handles missing fields gracefully."""
    # Create a copy of the response with some fields removed
    modified_response = deepcopy(GET_DEVICE_CHANNEL_RESPONSE)
    del modified_response["fields"]["label"]
    del modified_response["fields"]["alarmHigh"]
    del modified_response["fields"]["minimum"]

    # Parse the modified response
    channel = _document_to_device_channel(modified_response)

    # Check that the missing fields are None
    assert channel.label is None
    assert channel.alarm_high is None
    assert channel.minimum is None

    # Check that other fields are still present
    assert channel.value is not None
    assert channel.units is not None


def test_device_channel_additional_properties():
    """Test that the DeviceChannel model handles additional properties correctly."""
    # Create a copy of the response with an additional field
    modified_response = deepcopy(GET_DEVICE_CHANNEL_RESPONSE)
    modified_response["fields"]["newField"] = {"stringValue": "new value"}
    modified_response["fields"]["anotherNewField"] = {"integerValue": "42"}

    # Parse the modified response
    channel = _document_to_device_channel(modified_response)

    # Check that the additional properties are stored
    assert channel.additional_properties is not None
    assert "newField" in channel.additional_properties
    assert channel.additional_properties["newField"] == "new value"
    assert "anotherNewField" in channel.additional_properties
    assert channel.additional_properties["anotherNewField"] == "42"
