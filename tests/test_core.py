"""Test suite for the Core Thermoworks object."""

from datetime import datetime
from typing import Any
from unittest.mock import AsyncMock, patch
import pytest

from tests.core_test_object import CoreTestObject
from tests.test_data import (
    TEST_DEVICE_ID_0,
    TEST_DEVICE_ID_1,
    TEST_EMAIL_ADDRESS,
    TEST_ID_TOKEN,
    TEST_USER_ID,
    USER_RESPONSE,
    GET_DEVICE_RESPONSE,
    GET_DEVICE_CHANNEL_RESPONSE,
)
from thermoworks_cloud.auth import Auth
from thermoworks_cloud import ThermoworksCloud


def iso_instant(datetime_input: datetime) -> str:
    """Convert a datetime object to an ISO 8601 formatted 'instant' string.

    Args:
        datetime_input (datetime): The datetime object to convert.

    Returns:
        str: The ISO 8601 formatted string representation of the datetime object.
    """
    return datetime_input.isoformat(timespec="milliseconds").replace("+00:00", "Z")


def get_value(value_object: dict) -> Any:
    """Get the value from a nested dictionary.

    Args:
        value_object: The dictionary to search in

    Returns:
        The value at the specified field path
    """
    assert len(value_object) == 1, "Value object can only contain a single value"
    return list(value_object.values())[0]


def get_field_value(response_dict: dict, field_path: str):
    """Get a value from a nested dictionary using a field path.

    Args:
        response_dict: The dictionary to search in
        field_path: The path to the field, separated by dots

    Returns:
        The value at the specified field path
    """
    field_path_segments = field_path.split(".")
    fields = response_dict["fields"]
    for field_path_segment in field_path_segments:
        fields = fields[field_path_segment]

    return get_value(fields)


def assert_map_values(response_dict: dict, obj_dict: dict, field_path: str):
    """Compare boolean values from nested response dictionary with object dictionary

    Args:
        response_dict: The response dictionary containing mapValue fields
        obj_dict: The object dictionary to compare against
        field_path: The field path in response_dict to check
    """
    fields = response_dict["fields"][field_path]["mapValue"]["fields"]
    for key, value in fields.items():
        assert obj_dict[key] == get_value(value)


class TestCore:
    """Test class for ThermoworksCloud core functionality."""

    async def test_get_user(self, auth: Auth, core_test_object: CoreTestObject):
        """Test the get_user method of ThermoworksCloud.

        This test checks if the get_user method returns the expected User object
        when a valid user_id is provided.
        """

        # Setup
        core_test_object.expect_get_user(access_token=TEST_ID_TOKEN).respond_with_json(
            USER_RESPONSE
        )
        thermoworks_cloud = ThermoworksCloud(auth)

        # Act
        user = await thermoworks_cloud.get_user()

        # Assert
        assert user is not None
        assert user.uid == get_field_value(USER_RESPONSE, "uid")
        assert user.display_name == get_field_value(
            USER_RESPONSE, "displayName")
        assert user.email == get_field_value(USER_RESPONSE, "email")
        assert user.provider == get_field_value(USER_RESPONSE, "provider")
        assert user.time_zone == get_field_value(USER_RESPONSE, "timeZone")
        assert user.app_version == get_field_value(USER_RESPONSE, "appVersion")
        assert user.email_status == get_field_value(
            USER_RESPONSE, "emailStatus")
        assert user.preferred_units == get_field_value(
            USER_RESPONSE, "preferredUnits")
        assert user.locale == get_field_value(USER_RESPONSE, "locale")
        assert user.photo_url == get_field_value(USER_RESPONSE, "photoURL")
        assert user.use_24_time == get_field_value(USER_RESPONSE, "use24Time")
        assert_map_values(USER_RESPONSE, user.roles, "roles")
        assert_map_values(USER_RESPONSE, user.account_roles, "accountRoles")
        assert_map_values(USER_RESPONSE, user.system, "system")
        assert_map_values(
            USER_RESPONSE, user.notification_settings, "notificationSettings"
        )
        assert_map_values(USER_RESPONSE, user.fcm_tokens, "fcmTokens")

        # Devices
        device_order_items = user.device_order[TEST_USER_ID]
        assert len(device_order_items) == 2
        assert device_order_items[0].device_id == TEST_DEVICE_ID_0
        assert device_order_items[1].device_id == TEST_DEVICE_ID_1
        assert user.email_last_event is not None
        assert user.email_last_event.email == TEST_EMAIL_ADDRESS
        assert user.export_version == get_field_value(
            USER_RESPONSE, "exportVersion")
        assert user.last_seen_in_app == get_field_value(
            USER_RESPONSE, "lastSeenInApp")
        assert iso_instant(user.last_login) == get_field_value(
            USER_RESPONSE, "lastLogin"
        )
        assert iso_instant(user.create_time) == USER_RESPONSE["createTime"]
        assert iso_instant(user.update_time) == USER_RESPONSE["updateTime"]

    async def test_get_user_4xx_throws(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """Test the get_user method of ThermoworksCloud when a 4xx error is returned.

        Args:
            auth (Auth): A mock Auth object.
            core_test_object (CoreTestObject): A CoreTestObject instance.

        This test checks if the get_user method raises an exception when a 4xx error is returned.
        """
        # Setup
        core_test_object.expect_get_user(access_token=TEST_ID_TOKEN).respond_with_data(
            status=400, response_data=b"Bad Request"
        )
        thermoworks_cloud = ThermoworksCloud(auth)

        # Act
        with pytest.raises(RuntimeError):
            await thermoworks_cloud.get_user()

    async def test_get_user_5xx_throws(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """Test the get_user method of ThermoworksCloud when a 5xx error is returned.

        Args:
            auth (Auth): A mock Auth object.
            core_test_object (CoreTestObject): A CoreTestObject instance.

        This test checks if the get_user method raises an exception when a 5xx error is returned.
        """
        # Setup
        core_test_object.expect_get_user(access_token=TEST_ID_TOKEN).respond_with_data(
            status=500, response_data=b"Internal error"
        )
        thermoworks_cloud = ThermoworksCloud(auth)

        # Act
        with pytest.raises(RuntimeError):
            await thermoworks_cloud.get_user()

    async def test_get_user_exception_throws(self, auth: Auth):
        """This test checks if the get_user method raises an exception when an exceptions is
        thrown while processing the request.
        """
        # Setup
        with patch(
            "aiohttp.ClientSession.request", new_callable=AsyncMock
        ) as mock_function:
            mock_function.side_effect = RuntimeError("Simulated error")
            thermoworks_cloud = ThermoworksCloud(auth)

            # Act
            try:
                await thermoworks_cloud.get_user()
                assert False, "Should have raised an exception"
            except RuntimeError as e:
                assert str(e.__cause__) == "Simulated error"

    async def test_get_user_read_error_response_throws(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """Test the get_user method of ThermoworksCloud when an error is returned and the response
        cannot be read.

        Args:
            auth (Auth): A mock Auth object.
            core_test_object (CoreTestObject): A CoreTestObject instance.

        This test checks if the get_user method raises an exception is thrown while readin the
        body of the response
        """
        # Setup
        core_test_object.expect_get_user(access_token=TEST_ID_TOKEN).respond_with_data(
            status=400, response_data=b"Bad Request"
        )
        thermoworks_cloud = ThermoworksCloud(auth)
        with patch("aiohttp.ClientResponse.text", new_callable=AsyncMock) as get_text:
            get_text.side_effect = RuntimeError("Simulated error")
            thermoworks_cloud = ThermoworksCloud(auth)

            # Act
            with pytest.raises(RuntimeError):
                await thermoworks_cloud.get_user()

    async def test_get_device(self, auth: Auth, core_test_object: CoreTestObject):
        """Test the get_device method of ThermoworksCloud.

        Args:
            auth (Auth): A mock Auth object.
            core_test_object (CoreTestObject): A CoreTestObject instance.

        This test checks if the get_device method returns the expected Device object when a valid
        device serial number is provided.
        """
        # Setup
        core_test_object.expect_get_device(
            access_token=TEST_ID_TOKEN, device_serial=TEST_DEVICE_ID_0
        ).respond_with_json(GET_DEVICE_RESPONSE)
        thermoworks_cloud = ThermoworksCloud(auth)

        # Act
        device = await thermoworks_cloud.get_device(TEST_DEVICE_ID_0)

        # Assert
        # Test that each GET_DEVICE_RESPONSE property matches the Device object property
        assert device is not None
        assert device.battery_state == get_field_value(
            GET_DEVICE_RESPONSE, "batteryState"
        )
        assert device.big_query_info.dataset_id == get_field_value(
            GET_DEVICE_RESPONSE, "bigQuery.mapValue.fields.datasetId"
        )
        assert device.big_query_info.table_id == get_field_value(
            GET_DEVICE_RESPONSE, "bigQuery.mapValue.fields.tableId"
        )
        assert device.battery == int(
            get_field_value(GET_DEVICE_RESPONSE, "battery"))
        assert iso_instant(device.last_archive) == get_field_value(
            GET_DEVICE_RESPONSE, "lastArchive"
        )
        assert device.status == get_field_value(GET_DEVICE_RESPONSE, "status")
        assert iso_instant(device.last_wifi_connection) == get_field_value(
            GET_DEVICE_RESPONSE, "lastWifiConnection"
        )
        assert iso_instant(device.last_bluetooth_connection) == get_field_value(
            GET_DEVICE_RESPONSE, "lastBluetoothConnection"
        )
        assert device.type == get_field_value(GET_DEVICE_RESPONSE, "type")
        assert iso_instant(device.last_telemetry_saved) == get_field_value(
            GET_DEVICE_RESPONSE, "lastTelemetrySaved"
        )
        assert device.pending_load == get_field_value(
            GET_DEVICE_RESPONSE, "pendingLoad"
        )
        assert device.export_version == get_field_value(
            GET_DEVICE_RESPONSE, "exportVersion"
        )
        assert iso_instant(device.session_start) == get_field_value(
            GET_DEVICE_RESPONSE, "sessionStart"
        )
        assert device.device_id == get_field_value(
            GET_DEVICE_RESPONSE, "deviceId")
        assert device.serial == get_field_value(GET_DEVICE_RESPONSE, "serial")
        assert device.transmit_interval_in_seconds == int(
            get_field_value(GET_DEVICE_RESPONSE, "transmitIntervalInSeconds")
        )
        assert device.device_display_units == get_field_value(
            GET_DEVICE_RESPONSE, "deviceDisplayUnits"
        )
        assert device.iot_device_id == get_field_value(
            GET_DEVICE_RESPONSE, "iotDeviceId"
        )
        assert device.label == get_field_value(GET_DEVICE_RESPONSE, "label")
        assert iso_instant(device.last_purged) == get_field_value(
            GET_DEVICE_RESPONSE, "lastPurged"
        )
        assert device.battery_alert_sent == get_field_value(
            GET_DEVICE_RESPONSE, "batteryAlertSent"
        )
        assert device.color == get_field_value(GET_DEVICE_RESPONSE, "color")
        assert device.firmware == get_field_value(
            GET_DEVICE_RESPONSE, "firmware")
        assert device.thumbnail == get_field_value(
            GET_DEVICE_RESPONSE, "thumbnail")
        assert device.wifi_strength == int(
            get_field_value(GET_DEVICE_RESPONSE, "wifi_stength")
        )
        assert device.recording_interval_in_seconds == int(
            get_field_value(GET_DEVICE_RESPONSE, "recordingIntervalInSeconds")
        )
        assert device.account_id == get_field_value(
            GET_DEVICE_RESPONSE, "accountId")
        assert iso_instant(device.last_seen) == get_field_value(
            GET_DEVICE_RESPONSE, "lastSeen"
        )
        assert device.device_name == get_field_value(
            GET_DEVICE_RESPONSE, "device")

    async def test_get_device_4xx_throws(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """Test the get_device method of ThermoworksCloud when a 4xx error is returned.

        Args:
            auth (Auth): A mock Auth object.
            core_test_object (CoreTestObject): A CoreTestObject instance.

        This test checks if the get_device method raises an exception when a 4xx error is returned.
        """
        # Setup
        core_test_object.expect_get_device(
            access_token=TEST_ID_TOKEN, device_serial=TEST_DEVICE_ID_0
        ).respond_with_data(status=400, response_data=b"Bad Request")
        thermoworks_cloud = ThermoworksCloud(auth)

        # Act
        with pytest.raises(RuntimeError):
            await thermoworks_cloud.get_device(TEST_DEVICE_ID_0)

    async def test_get_device_5xx_throws(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """Test the get_device method of ThermoworksCloud when a 5xx error is returned.

        Args:
            auth (Auth): A mock Auth object.
            core_test_object (CoreTestObject): A CoreTestObject instance.

        This test checks if the get_device method raises an exception when a 4xx error is returned.
        """
        # Setup
        core_test_object.expect_get_device(
            access_token=TEST_ID_TOKEN, device_serial=TEST_DEVICE_ID_0
        ).respond_with_data(status=500, response_data=b"Internal error")
        thermoworks_cloud = ThermoworksCloud(auth)

        # Act
        with pytest.raises(RuntimeError):
            await thermoworks_cloud.get_device(TEST_DEVICE_ID_0)

    async def test_get_device_exception_throws(self, auth: Auth):
        """Test the get_device method of ThermoworksCloud when an exception is thrown
        Args:
            auth (Auth): A mock Auth object.

        This test checks if the get_device method raises an exception when an exception is thrown
        during an http request
        """
        # Setup
        with patch(
            "aiohttp.ClientSession.request", new_callable=AsyncMock
        ) as mock_request:
            mock_request.side_effect = RuntimeError("Simulated error")
            thermoworks_cloud = ThermoworksCloud(auth)

            # Act
            try:
                await thermoworks_cloud.get_device(TEST_DEVICE_ID_0)
                assert False, "Should have thrown an exception"
            except RuntimeError as e:
                assert str(e.__cause__) == "Simulated error"

    async def test_get_device_read_error_response_throws(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """This test checks if the get_device method raises an exception when an exception is thrown
        while reading the body of the response
        """
        # Setup

        core_test_object.expect_get_device(
            access_token=TEST_ID_TOKEN, device_serial=TEST_DEVICE_ID_0
        ).respond_with_data(status=500, response_data="Internal error")
        with patch("aiohttp.ClientResponse.text", new_callable=AsyncMock) as get_text:
            get_text.side_effect = RuntimeError("Simulated error")
            thermoworks_cloud = ThermoworksCloud(auth)

            # Act
            with pytest.raises(RuntimeError):
                await thermoworks_cloud.get_device(TEST_DEVICE_ID_0)

    async def test_get_device_channel(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """This test checks if the get_device_channel method returns the expected DeviceChannel 
        object when valid device serial and channel numbers are provided.
        """
        # Setup
        test_device_serial = "test_device_serial"
        test_device_channel = "test_device_channel"
        core_test_object.expect_get_device_channel(
            access_token=TEST_ID_TOKEN,
            device_serial=test_device_serial,
            channel=test_device_channel,
        ).respond_with_json(GET_DEVICE_CHANNEL_RESPONSE)
        thermoworks_cloud = ThermoworksCloud(auth)

        # Act
        channel = await thermoworks_cloud.get_device_channel(
            test_device_serial, test_device_channel
        )

        # Assert
        assert channel is not None
        assert iso_instant(channel.last_telemetry_saved) == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "lastTelemetrySaved"
        )
        assert channel.value == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "value")

        assert channel.minimum is not None
        assert iso_instant(channel.minimum.date_reading) == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "minimum.mapValue.fields.dateReading"
        )
        assert channel.minimum.reading.value == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE,
            "minimum.mapValue.fields.reading.mapValue.fields.value",
        )
        assert channel.minimum.reading.units == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE,
            "minimum.mapValue.fields.reading.mapValue.fields.units",
        )

        assert channel.units == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "units")
        assert channel.status == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "status")
        assert channel.type == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "type")
        assert channel.label == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "label")
        assert iso_instant(channel.last_seen) == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "lastSeen"
        )

        assert channel.alarm_high is not None
        assert channel.alarm_high.enabled == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "alarmHigh.mapValue.fields.enabled"
        )
        assert channel.alarm_high.units == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "alarmHigh.mapValue.fields.units"
        )
        assert channel.alarm_high.alarming == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "alarmHigh.mapValue.fields.alarming"
        )
        assert channel.alarm_high.value == int(
            get_field_value(
                GET_DEVICE_CHANNEL_RESPONSE, "alarmHigh.mapValue.fields.value"
            )
        )

        assert channel.number == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "number")
        assert channel.maximum is not None
        assert channel.maximum.reading.value == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE,
            "maximum.mapValue.fields.reading.mapValue.fields.value",
        )
        assert channel.maximum.reading.units == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE,
            "maximum.mapValue.fields.reading.mapValue.fields.units",
        )

        assert channel.alarm_low is not None
        assert channel.alarm_low.enabled == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "alarmLow.mapValue.fields.enabled"
        )
        assert channel.alarm_low.units == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "alarmLow.mapValue.fields.units"
        )
        assert channel.alarm_low.alarming == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "alarmLow.mapValue.fields.alarming"
        )
        assert channel.alarm_low.value == int(
            get_field_value(
                GET_DEVICE_CHANNEL_RESPONSE, "alarmLow.mapValue.fields.value"
            )
        )

        assert channel.show_avg_temp == get_field_value(
            GET_DEVICE_CHANNEL_RESPONSE, "showAvgTemp"
        )

    async def test_get_device_channel_4xx_throws(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """Test the get_device_channel method of ThermoworksCloud when a 4xx error is returned.

        Args:
            auth (Auth): A mock Auth object.
            core_test_object (CoreTestObject): A CoreTestObject instance.

        This test checks if the get_device_channel method raises an exception when a 4xx error
        is returned.
        """
        # Setup
        test_device_serial = "test_device_serial"
        test_device_channel = "test_device_channel"
        core_test_object.expect_get_device_channel(
            access_token=TEST_ID_TOKEN,
            device_serial=test_device_serial,
            channel=test_device_channel,
        ).respond_with_data(status=400, response_data=b"Bad Request")
        thermoworks_cloud = ThermoworksCloud(auth)

        # Act
        with pytest.raises(RuntimeError):
            await thermoworks_cloud.get_device_channel(
                test_device_serial, test_device_channel
            )

    async def test_get_device_channel_5xx_throws(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """Test the get_device_channel method of ThermoworksCloud when a 5xx error is returned.

        Args:
            auth (Auth): A mock Auth object.
            core_test_object (CoreTestObject): A CoreTestObject instance.

        This test checks if the get_device_channel method raises an exception when a 5xx error
        is returned.
        """
        # Setup
        test_device_serial = "test_device_serial"
        test_device_channel = "test_device_channel"
        core_test_object.expect_get_device_channel(
            access_token=TEST_ID_TOKEN,
            device_serial=test_device_serial,
            channel=test_device_channel,
        ).respond_with_data(status=500, response_data=b"Internal error")
        thermoworks_cloud = ThermoworksCloud(auth)

        # Act
        with pytest.raises(RuntimeError):
            await thermoworks_cloud.get_device_channel(
                test_device_serial, test_device_channel
            )

    async def test_get_device_channel_exception_throws(self, auth: Auth):
        """Test the get_device_channel method of ThermoworksCloud when an exception is thrown
        Args:
            auth (Auth): A mock Auth object.

        This test checks if the get_device_channel method raises an exception when an exception is
        thrown during an http request
        """
        # Setup
        with patch(
            "aiohttp.ClientSession.request", new_callable=AsyncMock
        ) as mock_function:
            mock_function.side_effect = RuntimeError("Something went wrong")
            thermoworks_cloud = ThermoworksCloud(auth)

            # Act
            try:
                await thermoworks_cloud.get_device_channel(
                    "test_device_serial", "test_device_channel"
                )
                assert False, "Should have thrown an exception"
            except RuntimeError as e:
                assert str(e.__cause__) == "Something went wrong"

    async def test_get_device_channel_read_error_response_throws(
        self, auth: Auth, core_test_object: CoreTestObject
    ):
        """This test checks if the get_device_channel method raises an exception when an exception
        is thrown while reading the body of the response
        """
        # Setup
        test_device_serial = "test_device_serial"
        test_device_channel = "test_device_channel"
        core_test_object.expect_get_device_channel(
            access_token=TEST_ID_TOKEN,
            device_serial=test_device_serial,
            channel=test_device_channel,
        ).respond_with_data(status=500, response_data="Internal error")
        with patch("aiohttp.ClientResponse.text", new_callable=AsyncMock) as get_text:
            get_text.side_effect = RuntimeError("Simulated error")
            thermoworks_cloud = ThermoworksCloud(auth)

            # Act
            with pytest.raises(RuntimeError):
                await thermoworks_cloud.get_device_channel(
                    test_device_serial, test_device_channel
                )
