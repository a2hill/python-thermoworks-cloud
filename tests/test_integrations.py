"""Tests for the ThermoWorks integrations API client."""

import json

import pytest

from thermoworks_cloud import (
    IntegrationsAuthenticationError,
    IntegrationsRateLimitError,
    ThermoworksIntegrationsClient,
)


DEVICE_RESPONSE = {
    "generatedAt": "2026-11-03T12:00:00Z",
    "devices": [
        {
            "id": "device-1",
            "serial": "serial-1",
            "label": "Kitchen",
            "type": "NODE",
            "model": "NODE",
            "displayUnits": "F",
            "battery": 87,
            "batteryState": "GOOD",
            "wifiSignal": -50,
            "gatewaySignal": -55,
            "lastSeen": "2026-11-03T11:59:00Z",
            "transmitIntervalSeconds": 60,
            "channels": [
                {
                    "id": "channel-1",
                    "number": 1,
                    "label": "Food",
                    "type": "temperature",
                    "enabled": True,
                    "value": 165.5,
                    "units": "F",
                    "status": "NORMAL",
                    "probeFailed": False,
                    "lastTelemetrySaved": "2026-11-03T11:58:30Z",
                    "alarmHigh": {"enabled": True, "value": 200, "alarming": False},
                    "alarmLow": None,
                }
            ],
        }
    ],
}


async def test_get_me_uses_bearer_auth(client_session, httpserver):
    httpserver.expect_request(
        "/v1/me",
        method="GET",
        headers={"Authorization": "Bearer twk_test", "Accept": "application/json"},
    ).respond_with_json({"accountId": "account-1"})

    client = ThermoworksIntegrationsClient(
        client_session, "twk_test", base_url=f"http://{httpserver.host}:{httpserver.port}"
    )
    assert await client.get_me() == {"accountId": "account-1"}


async def test_get_devices_maps_models_and_channels(client_session, httpserver):
    httpserver.expect_request(
        "/v1/devices", method="GET", headers={"Authorization": "Bearer twk_test"}
    ).respond_with_json(DEVICE_RESPONSE, headers={"ETag": '"snapshot-1"'})

    client = ThermoworksIntegrationsClient(
        client_session, "twk_test", base_url=f"http://{httpserver.host}:{httpserver.port}"
    )
    devices = await client.get_devices()

    assert len(devices) == 1
    assert devices[0].device_id == "device-1"
    assert devices[0].signal_strength == -55
    channels = client.get_device_channels("device-1")
    assert channels[0].number == "1"
    assert channels[0].value == 165.5
    assert channels[0].alarm_high is not None
    assert channels[0].additional_properties == {
        "enabled": True,
        "probeFailed": False,
    }


async def test_get_devices_uses_etag_and_cached_snapshot(client_session, httpserver):
    httpserver.expect_request("/v1/devices", method="GET").respond_with_json(
        DEVICE_RESPONSE, headers={"ETag": '"snapshot-1"'}
    )
    httpserver.expect_request(
        "/v1/devices",
        method="GET",
        headers={"If-None-Match": '"snapshot-1"'},
    ).respond_with_data(status=304)

    client = ThermoworksIntegrationsClient(
        client_session, "twk_test", base_url=f"http://{httpserver.host}:{httpserver.port}"
    )
    first = await client.get_devices()
    second = await client.get_devices()
    assert second[0].device_id == first[0].device_id


@pytest.mark.parametrize("status", [401, 403])
async def test_auth_errors_are_typed(client_session, httpserver, status):
    httpserver.expect_request("/v1/devices").respond_with_data(status=status)
    client = ThermoworksIntegrationsClient(
        client_session, "twk_test", base_url=f"http://{httpserver.host}:{httpserver.port}"
    )
    with pytest.raises(IntegrationsAuthenticationError):
        await client.get_devices()


async def test_rate_limit_exposes_retry_after(client_session, httpserver):
    httpserver.expect_request("/v1/devices").respond_with_data(
        status=429, headers={"Retry-After": "12"}
    )
    client = ThermoworksIntegrationsClient(
        client_session, "twk_test", base_url=f"http://{httpserver.host}:{httpserver.port}"
    )
    with pytest.raises(IntegrationsRateLimitError) as error:
        await client.get_devices()
    assert error.value.retry_after == 12


async def test_malformed_devices_response_is_rejected(client_session, httpserver):
    httpserver.expect_request("/v1/devices").respond_with_data(
        response_data=json.dumps({"generatedAt": "2026-11-03T12:00:00Z"}),
        content_type="application/json",
    )
    client = ThermoworksIntegrationsClient(
        client_session, "twk_test", base_url=f"http://{httpserver.host}:{httpserver.port}"
    )
    with pytest.raises(Exception, match="devices array"):
        await client.get_devices()
