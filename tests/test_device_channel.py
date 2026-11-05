"""Test suite for ThermoWorks device channels."""

from datetime import datetime

from aiohttp import ClientSession
import pytest

from tests.client_test_object import ClientTestObject
from tests.client_test_data import (
    GET_DEVICES_API_RESPONSE,
    GET_DEVICES_API_DISTINCT_CHANNEL_ID_RESPONSE,
    GET_DEVICES_API_LOW_CHANNEL_RESPONSE,
    GET_DEVICES_API_UNKNOWN_CHANNEL_STATUS_RESPONSE,
    GET_DEVICES_API_DISABLED_CHANNEL_RESPONSE,
    GET_DEVICES_API_FAILED_PROBE_RESPONSE,
    GET_DEVICES_API_ALARMING_CHANNEL_RESPONSE,
    GET_DEVICES_API_MISSING_CHANNEL_FLAGS_RESPONSE,
    GET_DEVICES_API_NO_PROBE_RESPONSE,
    GET_DEVICES_API_CELSIUS_DISPLAY_RESPONSE,
    GET_DEVICES_API_NULL_DISPLAY_UNITS_RESPONSE,
    GET_DEVICES_API_MISSING_DISPLAY_UNITS_RESPONSE,
    TEST_THERMOWORKS_API_KEY,
)
from tests.core_test_object import CoreTestObject
from tests.test_data import (
    GET_RFX_AIR_PROBE_CHANNEL_RESPONSE,
    GET_SIGNALS_CHANNEL_RESPONSE,
    TEST_ID_TOKEN,
)
from thermoworks_cloud import ThermoworksClient, ThermoworksCloud
from thermoworks_cloud.models import ChannelStatus
from thermoworks_cloud.models.device import DevicesResponse
from thermoworks_cloud.auth import Auth


def iso_instant(datetime_input: datetime) -> str:
    """Format a model timestamp for comparison with the response fixture."""
    return datetime_input.isoformat(timespec="milliseconds").replace("+00:00", "Z")


async def _get_channel_from_response(
    auth: Auth, core_test_object: CoreTestObject, response: dict
):
    """Return a parsed device channel from a mocked response."""
    core_test_object.expect_get_device_channel(
        access_token=TEST_ID_TOKEN,
        device_serial="test_device_serial",
        channel="1",
    ).respond_with_json(response)

    thermoworks_cloud = ThermoworksCloud(auth)
    return await thermoworks_cloud.get_device_channel("test_device_serial", "1")


async def test_get_rfx_air_probe_channel_alarms(
    auth: Auth, core_test_object: CoreTestObject
):
    """Test parsing RFX Air Probe alarms."""
    channel = await _get_channel_from_response(
        auth, core_test_object, GET_RFX_AIR_PROBE_CHANNEL_RESPONSE
    )

    assert channel.type == "Pro-Series"
    assert channel.label == "Grid Temperature"
    assert channel.status == "LOW"
    assert channel.alarm_high is not None
    assert channel.alarm_high.enabled is True
    assert channel.alarm_high.alarming is False
    assert channel.alarm_high.value == 175
    assert channel.alarm_high.units == "F"
    assert channel.alarm_low is not None
    assert channel.alarm_low.enabled is True
    assert channel.alarm_low.alarming is True
    assert channel.alarm_low.value == 125
    assert channel.alarm_low.units == "F"
    assert channel.additional_properties is not None
    assert (
        channel.additional_properties["estimatedAlarmStatus"]
        == "Alarm needs to be set to calculate estimated time"
    )


async def test_get_signals_channel(
    auth: Auth, core_test_object: CoreTestObject
):
    """Test parsing a Signals channel with an integer channel number."""
    channel = await _get_channel_from_response(
        auth, core_test_object, GET_SIGNALS_CHANNEL_RESPONSE
    )

    assert channel.number == "1"
    assert channel.value == 69.8
    assert channel.units == "F"
    assert channel.type == "pro series"
    assert channel.status == "NORMAL"


async def test_celsius_alarms_with_fahrenheit_readings(
    client_session: ClientSession, client_test_object: ClientTestObject
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


@pytest.mark.parametrize(
    "response",
    [
        pytest.param(GET_DEVICES_API_DISABLED_CHANNEL_RESPONSE, id="disabled"),
        pytest.param(GET_DEVICES_API_FAILED_PROBE_RESPONSE, id="probe-failed"),
        pytest.param(GET_DEVICES_API_ALARMING_CHANNEL_RESPONSE, id="alarming"),
    ],
)
async def test_channel_flags_are_mapped_to_model_fields(
    client_session: ClientSession,
    client_test_object: ClientTestObject,
    response: DevicesResponse,
) -> None:
    """Map true and false flags into fields rather than additional properties."""

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
    assert channel.id == expected["id"]
    assert channel.additional_properties is None


async def test_missing_channel_flags_remain_unknown(
    client_session: ClientSession, client_test_object: ClientTestObject
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
    client_session: ClientSession, client_test_object: ClientTestObject
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
    assert channel.status == ChannelStatus.NO_PROBE
    assert channel.value == expected["value"]
    assert channel.enabled == expected["enabled"]
    assert channel.probe_failed == expected["probeFailed"]
    assert channel.last_telemetry_saved is not None
    assert iso_instant(channel.last_telemetry_saved) == expected["lastTelemetrySaved"]
    assert device.last_seen is not None
    assert iso_instant(device.last_seen) == expected_device["lastSeen"]
    assert channel.last_telemetry_saved < device.last_seen


@pytest.mark.parametrize(
    ("response", "status"),
    [
        pytest.param(GET_DEVICES_API_RESPONSE, ChannelStatus.NORMAL, id="normal"),
        pytest.param(GET_DEVICES_API_LOW_CHANNEL_RESPONSE, ChannelStatus.LOW, id="low"),
        pytest.param(GET_DEVICES_API_NO_PROBE_RESPONSE, ChannelStatus.NO_PROBE, id="no-probe"),
    ],
)
async def test_channel_status_supports_named_comparisons(
    client_session: ClientSession, client_test_object: ClientTestObject,
    response: DevicesResponse, status: ChannelStatus,
) -> None:
    """Expose comparison constants without changing the returned status type."""

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
    assert channel.status == expected["status"]
    assert channel.status == status
    assert not isinstance(channel.status, ChannelStatus)


async def test_unknown_channel_status_and_additional_fields_are_preserved(
    client_session: ClientSession, client_test_object: ClientTestObject
) -> None:
    """Future status strings remain readable, and genuinely unmodeled fields remain additional."""

    # Setup
    client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
        GET_DEVICES_API_UNKNOWN_CHANNEL_STATUS_RESPONSE
    )
    client = ThermoworksClient(
        client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
    )
    expected = GET_DEVICES_API_UNKNOWN_CHANNEL_STATUS_RESPONSE["devices"][0]["channels"][0]

    # Act
    device = (await client.get_devices())[0]

    # Assert
    assert device.channels is not None
    channel = device.channels[0]
    assert channel.status == expected["status"]
    assert channel.id == expected["id"]
    assert channel.additional_properties == {
        "futureField": expected["futureField"],
    }


async def test_channel_id_and_number_are_independent(
    client_session: ClientSession, client_test_object: ClientTestObject
) -> None:
    """Map an opaque channel id separately from the existing channel-number representation."""

    # Setup
    client_test_object.expect_get_devices(TEST_THERMOWORKS_API_KEY).respond_with_json(
        GET_DEVICES_API_DISTINCT_CHANNEL_ID_RESPONSE
    )
    client = ThermoworksClient(
        client_session, TEST_THERMOWORKS_API_KEY, client_test_object.base_url
    )
    expected = GET_DEVICES_API_DISTINCT_CHANNEL_ID_RESPONSE["devices"][0]["channels"][0]

    # Act
    device = (await client.get_devices())[0]

    # Assert
    assert device.channels is not None
    channel = device.channels[0]
    assert channel.id == expected["id"]
    assert channel.number == str(expected["number"])
    assert channel.id != channel.number
    assert channel.additional_properties is None
