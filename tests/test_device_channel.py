"""Test suite for ThermoWorks device channels."""

from tests.core_test_object import CoreTestObject
from tests.test_data import (
    GET_RFX_AIR_PROBE_CHANNEL_RESPONSE,
    GET_SIGNALS_CHANNEL_RESPONSE,
    TEST_ID_TOKEN,
)
from thermoworks_cloud import ThermoworksCloud
from thermoworks_cloud.auth import Auth


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
