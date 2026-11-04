"""Test suite for the ThermoworksClient object, which reads the ThermoWorks API.

`test_core.py` covers `ThermoworksCloud`, which reads Firebase. The two share nothing except the
models they return, so these tests can stay when the Firebase implementation is removed.
"""

from datetime import datetime

from aiohttp import ClientSession
import pytest

from tests.client_test_object import ClientTestObject
from tests.client_test_data import (
    ERROR_RESPONSE,
    GET_DEVICES_API_NULLS_RESPONSE,
    GET_DEVICES_API_RESPONSE,
    GET_DEVICES_API_WITH_GATEWAY_AND_FAN_RESPONSE,
    GET_ME_RESPONSE,
    TEST_ETAG,
    TEST_REFRESHED_ETAG,
    TEST_THERMOWORKS_API_KEY,
)
from thermoworks_cloud import ApiAuthenticationError, RateLimitError, ThermoworksClient


def iso_instant(datetime_input: datetime) -> str:
    """Convert a datetime object to an ISO 8601 formatted 'instant' string.

    Args:
        datetime_input (datetime): The datetime object to convert.

    Returns:
        str: The ISO 8601 formatted string representation of the datetime object.
    """
    return datetime_input.isoformat(timespec="milliseconds").replace("+00:00", "Z")


class TestClient:
    """Test class for ThermoworksClient functionality."""

    async def test_get_me(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that get_me returns the account described by the response."""

        # Setup
        client_test_object.expect_get_me(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_ME_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        account = await client.get_me()

        # Assert
        assert account.account_id == GET_ME_RESPONSE["accountId"]
        assert account.api_key.id == GET_ME_RESPONSE["apiKey"]["id"]
        assert account.api_key.name == GET_ME_RESPONSE["apiKey"]["name"]
        assert account.api_key.scopes == GET_ME_RESPONSE["apiKey"]["scopes"]
        assert account.api_key.device_ids == GET_ME_RESPONSE["apiKey"]["deviceIds"]
        assert account.plan.id == GET_ME_RESPONSE["plan"]["id"]
        assert account.plan.api_tier == GET_ME_RESPONSE["plan"]["apiTier"]
        assert account.rate_limit.per_minute == GET_ME_RESPONSE["rateLimit"]["perMinute"]
        assert account.rate_limit.per_day == GET_ME_RESPONSE["rateLimit"]["perDay"]
        assert account.recommended_poll_seconds == GET_ME_RESPONSE["recommendedPollSeconds"]

    async def test_get_me_empty_response(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that get_me handles a response without any of the optional fields."""

        # Setup
        client_test_object.expect_get_me(TEST_THERMOWORKS_API_KEY).respond_with_json({})
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        account = await client.get_me()

        # Assert
        assert account.account_id is None
        assert account.api_key is None
        assert account.plan is None
        assert account.rate_limit is None

    async def test_get_devices(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that get_devices maps the response onto the existing Device model."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected = GET_DEVICES_API_RESPONSE["devices"][0]

        # Act
        devices = await client.get_devices()

        # Assert
        assert len(devices) == 1
        device = devices[0]
        assert device.device_id == expected["id"]
        assert device.serial == expected["serial"]
        assert device.label == expected["label"]
        assert device.device_name == expected["model"]
        assert device.device_display_units == expected["displayUnits"]
        assert device.type == expected["type"]
        assert device.firmware == expected["firmware"]
        assert device.battery == expected["battery"]
        assert device.battery_state == expected["batteryState"]
        assert device.fan is None
        assert device.wifi_strength == expected["wifiSignal"]
        assert device.gateway_rssi is None
        assert device.signal_strength == expected["wifiSignal"]
        assert iso_instant(device.last_seen) == expected["lastSeen"]
        assert device.transmit_interval_in_seconds == expected["transmitIntervalSeconds"]
        assert device.additional_properties == {
            "locationId": expected["locationId"],
            "nextExpectedConnection": expected["nextExpectedConnection"],
        }

    async def test_get_devices_channels(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that get_devices maps nested channels onto the existing DeviceChannel model."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected = GET_DEVICES_API_RESPONSE["devices"][0]["channels"][0]

        # Act
        devices = await client.get_devices()

        # Assert
        assert len(devices[0].channels) == 1
        channel = devices[0].channels[0]
        assert channel.number == str(expected["number"])
        assert channel.label == expected["label"]
        assert channel.type == expected["type"]
        assert channel.value == expected["value"]
        assert channel.units == expected["units"]
        assert channel.status == expected["status"]
        assert iso_instant(channel.last_telemetry_saved) == expected["lastTelemetrySaved"]
        assert iso_instant(channel.last_seen) == expected["lastSeen"]
        assert channel.additional_properties == {
            "id": expected["id"],
            "enabled": expected["enabled"],
            "alarming": expected["alarming"],
            "probeFailed": expected["probeFailed"],
        }

    async def test_get_devices_channel_alarms_use_channel_units(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that alarms, which have no units in the API, get the units of their channel."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected = GET_DEVICES_API_RESPONSE["devices"][0]["channels"][0]

        # Act
        channel = (await client.get_devices())[0].channels[0]

        # Assert
        assert channel.alarm_high.enabled == expected["alarmHigh"]["enabled"]
        assert channel.alarm_high.alarming == expected["alarmHigh"]["alarming"]
        assert channel.alarm_high.value == expected["alarmHigh"]["value"]
        assert channel.alarm_high.units == expected["units"]
        assert channel.alarm_low.enabled == expected["alarmLow"]["enabled"]
        assert channel.alarm_low.alarming == expected["alarmLow"]["alarming"]
        assert channel.alarm_low.value == expected["alarmLow"]["value"]
        assert channel.alarm_low.units == expected["units"]

    async def test_get_devices_channel_min_max_use_channel_units(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that extremes, which are bare numbers in the API, map to MinMaxReading."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected = GET_DEVICES_API_RESPONSE["devices"][0]["channels"][0]

        # Act
        channel = (await client.get_devices())[0].channels[0]

        # Assert
        assert channel.minimum.reading.value == expected["minimum"]
        assert channel.minimum.reading.units == expected["units"]
        assert channel.minimum.date_reading is None
        assert channel.maximum.reading.value == expected["maximum"]
        assert channel.maximum.reading.units == expected["units"]
        assert channel.maximum.date_reading is None

    async def test_get_devices_with_gateway_and_fan(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that gateway signal and fan accessories map onto the existing Device model."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_WITH_GATEWAY_AND_FAN_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected = GET_DEVICES_API_WITH_GATEWAY_AND_FAN_RESPONSE["devices"][0]

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.gateway_rssi == expected["gatewaySignal"]
        assert device.signal_strength == expected["gatewaySignal"]
        assert device.fan.connected == expected["fan"]["connected"]
        assert device.fan.connection == expected["fan"]["connection"]
        assert device.fan.fan_channel == expected["fan"]["fan_channel"]
        assert device.fan.set_temp == expected["fan"]["setTemp"]
        assert device.fan.state == expected["fan"]["state"]

    async def test_get_devices_null_fields(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that null and absent fields are left unset rather than failing the request."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_NULLS_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.serial is None
        assert device.last_seen is None
        channel = device.channels[0]
        assert channel.number is None
        assert channel.alarm_high is None
        assert channel.alarm_low is None
        assert channel.minimum is None
        assert channel.maximum is None
        assert channel.last_telemetry_saved is None

    async def test_get_devices_not_modified_returns_previous_devices(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that a 304 response to the previous ETag returns the previous devices."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RESPONSE, headers={"ETag": TEST_ETAG}
        )
        client_test_object.expect_get_devices(
            TEST_THERMOWORKS_API_KEY, etag=TEST_ETAG
        ).respond_with_data(status=304)
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        previous_devices = await client.get_devices()

        # Act
        devices = await client.get_devices()

        # Assert
        assert devices == previous_devices

    async def test_get_devices_sends_latest_etag(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that a changed response replaces the devices and the ETag sent next."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RESPONSE, headers={"ETag": TEST_ETAG}
        )
        client_test_object.expect_get_devices(
            TEST_THERMOWORKS_API_KEY, etag=TEST_ETAG
        ).respond_with_json(
            GET_DEVICES_API_WITH_GATEWAY_AND_FAN_RESPONSE, headers={"ETag": TEST_REFRESHED_ETAG}
        )
        client_test_object.expect_get_devices(
            TEST_THERMOWORKS_API_KEY, etag=TEST_REFRESHED_ETAG
        ).respond_with_data(status=304)
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        await client.get_devices()
        refreshed_devices = await client.get_devices()

        # Act
        devices = await client.get_devices()

        # Assert
        assert devices == refreshed_devices
        assert devices[0].gateway_rssi == (
            GET_DEVICES_API_WITH_GATEWAY_AND_FAN_RESPONSE["devices"][0]["gatewaySignal"]
        )

    @pytest.mark.parametrize("status", [401, 403])
    async def test_get_me_rejected_key_throws(
        self, client_session: ClientSession, client_test_object: ClientTestObject, status: int
    ):
        """Test that get_me raises ApiAuthenticationError when the key is rejected."""

        # Setup
        client_test_object.expect_get_me(TEST_THERMOWORKS_API_KEY).respond_with_json(
            ERROR_RESPONSE, status=status
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        with pytest.raises(ApiAuthenticationError):
            await client.get_me()

    @pytest.mark.parametrize("status", [401, 403])
    async def test_get_devices_rejected_key_throws(
        self, client_session: ClientSession, client_test_object: ClientTestObject, status: int
    ):
        """Test that get_devices raises ApiAuthenticationError when the key is rejected."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            ERROR_RESPONSE, status=status
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        with pytest.raises(ApiAuthenticationError):
            await client.get_devices()

    async def test_get_devices_rate_limited_throws(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that the wait requested by a 429 response is available to the caller."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_data(
            status=429, headers={"Retry-After": "12"}
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        with pytest.raises(RateLimitError) as error:
            await client.get_devices()

        # Assert
        assert error.value.retry_after == 12

    @pytest.mark.parametrize("status", [400, 404, 500])
    async def test_get_me_error_throws(
        self, client_session: ClientSession, client_test_object: ClientTestObject, status: int
    ):
        """Test that get_me raises a RuntimeError for any other failed response."""

        # Setup
        client_test_object.expect_get_me(TEST_THERMOWORKS_API_KEY).respond_with_data(
            status=status, response_data=b"Error"
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        with pytest.raises(RuntimeError):
            await client.get_me()

    @pytest.mark.parametrize("status", [400, 404, 500])
    async def test_get_devices_error_throws(
        self, client_session: ClientSession, client_test_object: ClientTestObject, status: int
    ):
        """Test that get_devices raises a RuntimeError for any other failed response."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_data(
            status=status, response_data=b"Error"
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        with pytest.raises(RuntimeError):
            await client.get_devices()

    async def test_get_devices_raw(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that get_devices_raw returns the response without parsing it."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        response = await client.get_devices_raw()

        # Assert
        assert response == GET_DEVICES_API_RESPONSE

    async def test_get_devices_raw_error_throws(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ):
        """Test that get_devices_raw raises a RuntimeError for a failed response."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_data(
            status=500, response_data=b"Error"
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        with pytest.raises(RuntimeError):
            await client.get_devices_raw()
