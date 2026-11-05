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
    GET_DEVICES_API_DISABLED_CHANNEL_RESPONSE,
    GET_DEVICES_API_FAILED_PROBE_RESPONSE,
    GET_DEVICES_API_ALARMING_CHANNEL_RESPONSE,
    GET_DEVICES_API_MISSING_CHANNEL_FLAGS_RESPONSE,
    GET_DEVICES_API_NO_PROBE_RESPONSE,
    GET_DEVICES_API_CELSIUS_DISPLAY_RESPONSE,
    GET_DEVICES_API_NULL_DISPLAY_UNITS_RESPONSE,
    GET_DEVICES_API_MISSING_DISPLAY_UNITS_RESPONSE,
    GET_DEVICES_API_RFX_GATEWAY_RESPONSE,
    GET_DEVICES_API_RFX_MEAT_RESPONSE,
    GET_DEVICES_API_BILLOWS_PAUSED_RESPONSE,
    GET_DEVICES_API_BILLOWS_PULSING_RESPONSE,
    GET_DEVICES_API_BILLOWS_DISCONNECTED_RESPONSE,
    GET_DEVICES_API_BILLOWS_DISCONNECTED_BLOWING_RESPONSE,
    GET_DEVICES_API_BILLOWS_DISCONNECTED_PULSING_RESPONSE,
    GET_DEVICES_API_BILLOWS_UNKNOWN_RESPONSE,
    GET_DEVICES_API_BILLOWS_NULL_STATE_RESPONSE,
    GET_ME_RESPONSE,
    TEST_ETAG,
    TEST_REFRESHED_ETAG,
    TEST_THERMOWORKS_API_KEY,
)
from thermoworks_cloud import ApiAuthenticationError, RateLimitError, ThermoworksClient
from thermoworks_cloud.models import FanState
from thermoworks_cloud.models.device import DevicesResponse


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
    ) -> None:
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
        assert account.api_key is not None
        assert account.api_key.id == GET_ME_RESPONSE["apiKey"]["id"]
        assert account.api_key.name == GET_ME_RESPONSE["apiKey"]["name"]
        assert account.api_key.scopes == GET_ME_RESPONSE["apiKey"]["scopes"]
        assert account.api_key.device_ids == GET_ME_RESPONSE["apiKey"]["deviceIds"]
        assert account.plan is not None
        assert account.plan.id == GET_ME_RESPONSE["plan"]["id"]
        assert account.plan.api_tier == GET_ME_RESPONSE["plan"]["apiTier"]
        assert account.rate_limit is not None
        assert account.rate_limit.per_minute == GET_ME_RESPONSE["rateLimit"]["perMinute"]
        assert account.rate_limit.per_day == GET_ME_RESPONSE["rateLimit"]["perDay"]
        assert account.recommended_poll_seconds == GET_ME_RESPONSE["recommendedPollSeconds"]

    async def test_get_me_empty_response(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
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
    ) -> None:
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
        # Without a gateway signal, this is a Wi-Fi device reporting its Wi-Fi signal
        assert device.signal_strength == expected["wifiSignal"]
        assert device.last_seen is not None
        assert iso_instant(device.last_seen) == expected["lastSeen"]
        assert device.transmit_interval_in_seconds == expected["transmitIntervalSeconds"]
        assert device.additional_properties == {
            "locationId": expected["locationId"],
            "nextExpectedConnection": expected["nextExpectedConnection"],
        }

    async def test_get_devices_channels(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
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
        assert devices[0].channels is not None
        assert len(devices[0].channels) == 1
        channel = devices[0].channels[0]
        assert channel.number == str(expected["number"])
        assert channel.label == expected["label"]
        assert channel.type == expected["type"]
        assert channel.value == expected["value"]
        assert channel.units == expected["units"]
        assert channel.status == expected["status"]
        assert channel.enabled == expected["enabled"]
        assert channel.probe_failed == expected["probeFailed"]
        assert channel.alarming == expected["alarming"]
        assert channel.last_telemetry_saved is not None
        assert iso_instant(channel.last_telemetry_saved) == expected["lastTelemetrySaved"]
        assert channel.last_seen is not None
        assert iso_instant(channel.last_seen) == expected["lastSeen"]
        assert channel.additional_properties == {
            "id": expected["id"],
            "enabled": expected["enabled"],
            "alarming": expected["alarming"],
            "probeFailed": expected["probeFailed"],
        }

    async def test_get_devices_channel_alarms_use_device_display_units(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
        """Test that temperature alarm thresholds use the parent device display units."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected = GET_DEVICES_API_RESPONSE["devices"][0]["channels"][0]

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.channels is not None
        channel = device.channels[0]
        assert channel.alarm_high is not None
        assert channel.alarm_high.enabled == expected["alarmHigh"]["enabled"]
        assert channel.alarm_high.alarming == expected["alarmHigh"]["alarming"]
        assert channel.alarm_high.value == expected["alarmHigh"]["value"]
        assert channel.alarm_high.units == GET_DEVICES_API_RESPONSE["devices"][0]["displayUnits"]
        assert channel.alarm_low is not None
        assert channel.alarm_low.enabled == expected["alarmLow"]["enabled"]
        assert channel.alarm_low.alarming == expected["alarmLow"]["alarming"]
        assert channel.alarm_low.value == expected["alarmLow"]["value"]
        assert channel.alarm_low.units == GET_DEVICES_API_RESPONSE["devices"][0]["displayUnits"]

    async def test_get_devices_channel_min_max_use_channel_units(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
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
        device = (await client.get_devices())[0]

        # Assert
        assert device.channels is not None
        channel = device.channels[0]
        assert channel.minimum is not None
        assert channel.minimum.reading is not None
        assert channel.minimum.reading.value == expected["minimum"]
        assert channel.minimum.reading.units == expected["units"]
        assert channel.minimum.date_reading is None
        assert channel.maximum is not None
        assert channel.maximum.reading is not None
        assert channel.maximum.reading.value == expected["maximum"]
        assert channel.maximum.reading.units == expected["units"]
        assert channel.maximum.date_reading is None

    @pytest.mark.parametrize(
        ("response", "state", "state_name"),
        [
            pytest.param(
                GET_DEVICES_API_BILLOWS_PAUSED_RESPONSE, FanState.PAUSED, "Paused", id="paused"
            ),
            pytest.param(
                GET_DEVICES_API_RFX_GATEWAY_RESPONSE, FanState.BLOWING, "Blowing", id="blowing"
            ),
            pytest.param(
                GET_DEVICES_API_BILLOWS_PULSING_RESPONSE, FanState.PULSING, "Pulsing", id="pulsing"
            ),
        ],
    )
    async def test_get_devices_with_billows(
        self,
        client_session: ClientSession,
        client_test_object: ClientTestObject,
        response: DevicesResponse,
        state: FanState,
        state_name: str,
    ) -> None:
        """Compare the existing integer states against named enum values."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(response)
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        expected = response["devices"][0]
        expected_fan = expected["fan"]
        assert expected_fan is not None

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.device_name == expected["model"]
        assert device.wifi_strength == expected["wifiSignal"]
        assert device.gateway_rssi == expected["gatewaySignal"]
        assert device.signal_strength == expected["wifiSignal"]
        assert device.fan is not None
        assert device.fan.connected is True
        assert device.fan.connection is True
        assert device.fan.fan_channel == expected_fan["channel"]
        assert device.fan.set_temp == expected_fan["setTemp"]
        assert device.fan.state == state
        assert isinstance(device.fan.state, int)
        assert not isinstance(device.fan.state, FanState)
        assert device.fan.state_name == state_name

    @pytest.mark.parametrize(
        ("response", "state"),
        [
            pytest.param(
                GET_DEVICES_API_BILLOWS_DISCONNECTED_RESPONSE, FanState.PAUSED, id="paused"
            ),
            pytest.param(
                GET_DEVICES_API_BILLOWS_DISCONNECTED_BLOWING_RESPONSE,
                FanState.BLOWING,
                id="blowing",
            ),
            pytest.param(
                GET_DEVICES_API_BILLOWS_DISCONNECTED_PULSING_RESPONSE,
                FanState.PULSING,
                id="pulsing",
            ),
        ],
    )
    async def test_get_devices_disconnected_billows_retains_settings(
        self,
        client_session: ClientSession,
        client_test_object: ClientTestObject,
        response: DevicesResponse,
        state: FanState,
    ) -> None:
        """Retain the last reported state independently of the connection flag."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(response)
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        expected_fan = response["devices"][0]["fan"]
        assert expected_fan is not None

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.fan is not None
        assert device.fan.connected is False
        assert device.fan.connection is False
        assert device.fan.fan_channel == expected_fan["channel"]
        assert device.fan.set_temp == expected_fan["setTemp"]
        assert device.fan.state == state

    @pytest.mark.parametrize(
        "response",
        [
            pytest.param(GET_DEVICES_API_BILLOWS_UNKNOWN_RESPONSE, id="unknown"),
            pytest.param(GET_DEVICES_API_BILLOWS_NULL_STATE_RESPONSE, id="null"),
        ],
    )
    async def test_get_devices_unrecognized_billows_state(
        self,
        client_session: ClientSession,
        client_test_object: ClientTestObject,
        response: DevicesResponse,
    ) -> None:
        """Unknown or absent states remain readable instead of rejecting a device."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(response)
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected_fan = response["devices"][0]["fan"]
        assert expected_fan is not None

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.fan is not None
        assert device.fan.state == expected_fan["state"]
        assert not isinstance(device.fan.state, FanState)
        assert device.fan.state_name is None

    async def test_get_devices_rfx_meat_channels(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
        """Retain a meat probe's computed channel zero and all four physical channels."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RFX_MEAT_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        expected = GET_DEVICES_API_RFX_MEAT_RESPONSE["devices"][0]
        expected_channels = expected["channels"]

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.device_id == expected["id"]
        assert device.serial == expected["serial"]
        assert device.device_name == expected["model"]
        assert device.fan is None
        assert device.wifi_strength is None
        assert device.gateway_rssi == expected["gatewaySignal"]
        assert device.signal_strength == expected["gatewaySignal"]
        assert device.channels is not None
        assert [channel.number for channel in device.channels] == [
            str(channel["number"]) for channel in expected_channels
        ]
        assert [channel.type for channel in device.channels] == [
            channel["type"] for channel in expected_channels
        ]
        assert [channel.value for channel in device.channels] == [
            channel["value"] for channel in expected_channels
        ]
        assert [channel.units for channel in device.channels] == [
            channel["units"] for channel in expected_channels
        ]
        assert [
            iso_instant(channel.last_telemetry_saved) if channel.last_telemetry_saved else None
            for channel in device.channels
        ] == [channel["lastTelemetrySaved"] for channel in expected_channels]

    async def test_get_devices_null_fields(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
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
        assert device.channels is not None
        channel = device.channels[0]
        assert channel.number is None
        assert channel.alarm_high is None
        assert channel.alarm_low is None
        assert channel.minimum is None
        assert channel.maximum is None
        assert channel.last_telemetry_saved is None

    async def test_get_devices_not_modified_returns_previous_devices(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
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
    ) -> None:
        """Test that a changed response replaces the devices and the ETag sent next."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_RESPONSE, headers={"ETag": TEST_ETAG}
        )
        client_test_object.expect_get_devices(
            TEST_THERMOWORKS_API_KEY, etag=TEST_ETAG
        ).respond_with_json(
            GET_DEVICES_API_RFX_GATEWAY_RESPONSE, headers={"ETag": TEST_REFRESHED_ETAG}
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
        assert [device.device_id for device in devices] == [
            device["id"] for device in GET_DEVICES_API_RFX_GATEWAY_RESPONSE["devices"]
        ]

    @pytest.mark.parametrize("status", [401, 403])
    async def test_get_me_rejected_key_throws(
        self, client_session: ClientSession, client_test_object: ClientTestObject, status: int
    ) -> None:
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
    ) -> None:
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
    ) -> None:
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
    ) -> None:
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
    ) -> None:
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
    ) -> None:
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
    ) -> None:
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


class TestTemperatureAlarmUnits:
    """Regression coverage for temperature thresholds reported in device display units."""

    async def test_celsius_alarms_with_fahrenheit_readings(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
        """Keep readings and extrema in Fahrenheit while labelling thresholds in Celsius."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_CELSIUS_DISPLAY_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected_device = GET_DEVICES_API_CELSIUS_DISPLAY_RESPONSE["devices"][0]
        expected = expected_device["channels"][0]
        expected_high = expected["alarmHigh"]
        expected_low = expected["alarmLow"]
        assert expected_high is not None
        assert expected_low is not None

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.channels is not None
        channel = device.channels[0]
        assert channel.value == expected["value"]
        assert channel.units == expected["units"]
        assert channel.alarm_high is not None
        assert channel.alarm_high.value == expected_high["value"]
        assert channel.alarm_high.enabled == expected_high["enabled"]
        assert channel.alarm_high.alarming == expected_high["alarming"]
        assert channel.alarm_high.units == expected_device["displayUnits"]
        assert channel.alarm_low is not None
        assert channel.alarm_low.value == expected_low["value"]
        assert channel.alarm_low.enabled == expected_low["enabled"]
        assert channel.alarm_low.alarming == expected_low["alarming"]
        assert channel.alarm_low.units == expected_device["displayUnits"]
        assert channel.minimum is not None
        assert channel.minimum.reading is not None
        assert channel.minimum.reading.value == expected["minimum"]
        assert channel.minimum.reading.units == expected["units"]
        assert channel.maximum is not None
        assert channel.maximum.reading is not None
        assert channel.maximum.reading.value == expected["maximum"]
        assert channel.maximum.reading.units == expected["units"]

    @pytest.mark.parametrize(
        "response",
        [
            pytest.param(GET_DEVICES_API_NULL_DISPLAY_UNITS_RESPONSE, id="null"),
            pytest.param(GET_DEVICES_API_MISSING_DISPLAY_UNITS_RESPONSE, id="missing"),
        ],
    )
    async def test_missing_display_units_leave_alarm_units_unknown(
        self,
        client_session: ClientSession,
        client_test_object: ClientTestObject,
        response: DevicesResponse,
    ) -> None:
        """Do not guess temperature alarm units from the channel's measurement units."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(response)
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected = response["devices"][0]["channels"][0]
        expected_high = expected["alarmHigh"]
        expected_low = expected["alarmLow"]
        assert expected_high is not None
        assert expected_low is not None

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.channels is not None
        channel = device.channels[0]
        assert channel.value == expected["value"]
        assert channel.units == expected["units"]
        assert channel.alarm_high is not None
        assert channel.alarm_high.value == expected_high["value"]
        assert channel.alarm_high.units is None
        assert channel.alarm_low is not None
        assert channel.alarm_low.value == expected_low["value"]
        assert channel.alarm_low.units is None


class TestChannelMetadata:
    """Expose reported channel facts without imposing an availability or expiry policy."""

    @pytest.mark.parametrize(
        "response",
        [
            pytest.param(GET_DEVICES_API_DISABLED_CHANNEL_RESPONSE, id="disabled"),
            pytest.param(GET_DEVICES_API_FAILED_PROBE_RESPONSE, id="probe-failed"),
            pytest.param(GET_DEVICES_API_ALARMING_CHANNEL_RESPONSE, id="alarming"),
        ],
    )
    async def test_channel_flags_are_exposed_without_removing_additional_properties(
        self,
        client_session: ClientSession,
        client_test_object: ClientTestObject,
        response: DevicesResponse,
    ) -> None:
        """Expose both true and false flags while retaining the previous dictionary interface."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(response)
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected = response["devices"][0]["channels"][0]

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.channels is not None
        channel = device.channels[0]
        assert channel.enabled == expected["enabled"]
        assert channel.probe_failed == expected["probeFailed"]
        assert channel.alarming == expected["alarming"]
        assert channel.additional_properties is not None
        assert channel.additional_properties["enabled"] == expected["enabled"]
        assert channel.additional_properties["probeFailed"] == expected["probeFailed"]
        assert channel.additional_properties["alarming"] == expected["alarming"]

    async def test_missing_channel_flags_remain_unknown(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
        """Missing metadata must not be interpreted as a healthy or failed probe."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_MISSING_CHANNEL_FLAGS_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.channels is not None
        channel = device.channels[0]
        assert channel.enabled is None
        assert channel.probe_failed is None
        assert channel.alarming is None

    async def test_no_probe_preserves_status_and_measurement_timestamp(
        self, client_session: ClientSession, client_test_object: ClientTestObject
    ) -> None:
        """A live device and non-failing flags must not obscure an old channel measurement."""

        # Setup
        client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
            GET_DEVICES_API_NO_PROBE_RESPONSE
        )
        client = ThermoworksClient(
            client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
        )
        expected_device = GET_DEVICES_API_NO_PROBE_RESPONSE["devices"][0]
        expected = expected_device["channels"][0]

        # Act
        device = (await client.get_devices())[0]

        # Assert
        assert device.channels is not None
        channel = device.channels[0]
        assert channel.status == expected["status"]
        assert channel.value == expected["value"]
        assert channel.enabled == expected["enabled"]
        assert channel.probe_failed == expected["probeFailed"]
        assert channel.last_telemetry_saved is not None
        assert iso_instant(channel.last_telemetry_saved) == expected["lastTelemetrySaved"]
        assert device.last_seen is not None
        assert iso_instant(device.last_seen) == expected_device["lastSeen"]
        assert channel.last_telemetry_saved < device.last_seen
