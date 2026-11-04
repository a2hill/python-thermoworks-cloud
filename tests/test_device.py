"""Test suite for ThermoWorks devices."""

import pytest

from tests.core_test_object import CoreTestObject
from tests.test_data import (
    GET_DEVICE_FAN_STATE_RESPONSES,
    GET_DEVICE_WITH_DISCONNECTED_FAN_RESPONSE,
    GET_DEVICE_WITH_FAN_RESPONSE,
    GET_DEVICE_WITH_GATEWAY_RSSI_RESPONSE,
    TEST_DEVICE_ID_0,
    TEST_ID_TOKEN,
)
from thermoworks_cloud import ThermoworksCloud, ThermoworksClient
from thermoworks_cloud.auth import Auth


async def _get_device_from_response(
    auth: Auth, core_test_object: CoreTestObject, response: dict, api_client=None
):
    """Return a parsed device from a mocked response."""
    if api_client is not None:
        return await api_client.get_device(TEST_DEVICE_ID_0)
    core_test_object.expect_get_device(
        access_token=TEST_ID_TOKEN, device_serial=TEST_DEVICE_ID_0
    ).respond_with_json(response)

    return await ThermoworksCloud(auth).get_device(TEST_DEVICE_ID_0)


@pytest.mark.parametrize("backend", ["firebase", "api"])
async def test_get_device_with_gateway_rssi(
    auth: Auth,
    core_test_object: CoreTestObject,
    backend,
    client_session,
    httpserver,
    httpserver_endpoint,
):
    """Test parsing gateway RSSI from an RFX meat probe device."""
    api_client = None
    if backend == "api":
        httpserver.expect_request("/v1/devices").respond_with_json(
            {
                "devices": [
                    {
                        "id": TEST_DEVICE_ID_0,
                        "serial": TEST_DEVICE_ID_0,
                        "type": "rfx",
                        "model": "rfx meat",
                        "gatewaySignal": -55,
                        "channels": [],
                    }
                ]
            }
        )
        api_client = ThermoworksClient(client_session, "test-key", httpserver_endpoint)
    device = await _get_device_from_response(
        auth, core_test_object, GET_DEVICE_WITH_GATEWAY_RSSI_RESPONSE, api_client
    )

    assert device.gateway_rssi == -55
    assert device.signal_strength == -55
    assert device.additional_properties is None


async def test_get_device_with_fan(auth: Auth, core_test_object: CoreTestObject):
    """Test parsing a connected fan accessory from a device."""
    device = await _get_device_from_response(auth, core_test_object, GET_DEVICE_WITH_FAN_RESPONSE)

    assert device.fan is not None
    assert device.fan.connected is True
    assert device.fan.connection is True
    assert device.fan.fan_channel == "1"
    assert device.fan.set_temp == 150
    assert device.fan.state == 1
    assert device.fan.state_name == "Blowing"


@pytest.mark.parametrize(
    ("state", "state_name"),
    [
        (0, "Paused"),
        (1, "Blowing"),
        (2, "Pulsing"),
        (99, None),
    ],
)
async def test_get_device_fan_state_name(
    auth: Auth, core_test_object: CoreTestObject, state: int, state_name: str
):
    """Test fan state names observed in the ThermoWorks app."""
    device = await _get_device_from_response(
        auth, core_test_object, GET_DEVICE_FAN_STATE_RESPONSES[state]
    )

    assert device.fan is not None
    assert device.fan.state_name == state_name


async def test_get_device_with_disconnected_fan(auth: Auth, core_test_object: CoreTestObject):
    """Test parsing a fan accessory when it is present but disconnected."""
    device = await _get_device_from_response(
        auth, core_test_object, GET_DEVICE_WITH_DISCONNECTED_FAN_RESPONSE
    )

    assert device.fan is not None
    assert device.fan.connected is False
    assert device.fan.connection is False
    assert device.fan.fan_channel == "1"
    assert device.fan.set_temp is None
    assert device.fan.state is None
    assert device.fan.state_name is None
