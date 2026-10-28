"""Test suite for ThermoWorks device channels."""

from copy import deepcopy

import pytest

from tests.core_test_object import CoreTestObject
from tests.test_data import GET_RFX_AIR_PROBE_CHANNEL_RESPONSE, TEST_ID_TOKEN
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


@pytest.mark.parametrize(
    ("number_field", "expected_number"),
    [
        pytest.param({"stringValue": "1"}, "1", id="string-number"),
        pytest.param({"integerValue": "1"}, "1", id="signals-integer-number"),
        pytest.param(None, None, id="missing-number"),
    ],
)
async def test_get_channel_number(
    auth: Auth,
    core_test_object: CoreTestObject,
    number_field: dict | None,
    expected_number: str | None,
):
    """Normalize string and integer channel numbers while keeping missing numbers optional."""
    response = deepcopy(GET_RFX_AIR_PROBE_CHANNEL_RESPONSE)
    if number_field is None:
        response["fields"].pop("number", None)
    else:
        response["fields"]["number"] = number_field

    channel = await _get_channel_from_response(auth, core_test_object, response)

    assert channel.number == expected_number


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
