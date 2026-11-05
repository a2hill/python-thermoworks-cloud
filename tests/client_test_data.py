"""Test data for the ThermoworksClient tests."""

from copy import deepcopy
import json
from typing import Optional

from thermoworks_cloud.models import FanState
from thermoworks_cloud.models.device import DevicesResponse

# API key sent to the ThermoWorks API, which is not the Firebase `API_KEY`
TEST_THERMOWORKS_API_KEY = "twk_test_key_id_test_secret"
TEST_ETAG = 'W/"test-etag"'
TEST_REFRESHED_ETAG = 'W/"test-refreshed-etag"'

# Shape from the API documentation with invented values. No response has been captured for this
# endpoint.
GET_ME_RESPONSE = json.loads(
    """
{
  "accountId": "test-account-id",
  "apiKey": {
    "id": "test-key-id",
    "name": "Home Assistant",
    "scopes": ["read:devices"],
    "deviceIds": null
  },
  "plan": { "id": null, "apiTier": "free" },
  "rateLimit": { "perMinute": 4, "perDay": 3000 },
  "recommendedPollSeconds": 60
}"""
)

# Actual response value structure
GET_DEVICES_API_RESPONSE = json.loads(
    """
{
  "generatedAt": "2026-11-04T04:43:49.806Z",
  "devices": [
    {
      "id": "12:34:56:78:90:AB",
      "serial": "12:34:56:78:90:AB",
      "label": "NODE",
      "model": "node",
      "displayUnits": "F",
      "type": "datalogger",
      "firmware": "2.1.8-30",
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": -59,
      "gatewaySignal": null,
      "lastSeen": "2026-11-04T03:54:28.717Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 3600,
      "channels": [
        {
          "id": "1",
          "number": 1,
          "label": "Freezer",
          "type": "Pro-Series",
          "enabled": true,
          "value": -10.300000190734863,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": { "enabled": true, "value": 20, "alarming": false },
          "alarmLow": { "enabled": true, "value": -12, "alarming": false },
          "minimum": -13,
          "maximum": 69.5,
          "lastTelemetrySaved": "2026-11-04T03:55:17.000Z",
          "lastSeen": "2026-11-04T03:54:28.717Z"
        }
      ]
    }
  ]
}"""
)


def _response_with_units(*, display_units: Optional[str], channel_units: str) -> DevicesResponse:
    """Vary unit metadata independently; keep numeric readings and thresholds unchanged."""
    response = deepcopy(GET_DEVICES_API_RESPONSE)
    device = response["devices"][0]
    device["displayUnits"] = display_units
    device["channels"][0]["units"] = channel_units
    return response


# Representative variants, not full captures: mixed temperature units were reported at
# https://github.com/a2hill/ha-thermoworks-cloud/issues/46#issuecomment-6633350372
# Missing metadata exercises the mapping boundary independently.
GET_DEVICES_API_CELSIUS_DISPLAY_RESPONSE = _response_with_units(
    display_units="C", channel_units="F"
)
GET_DEVICES_API_NULL_DISPLAY_UNITS_RESPONSE = _response_with_units(
    display_units=None, channel_units="F"
)
GET_DEVICES_API_MISSING_DISPLAY_UNITS_RESPONSE = deepcopy(GET_DEVICES_API_RESPONSE)
del GET_DEVICES_API_MISSING_DISPLAY_UNITS_RESPONSE["devices"][0]["displayUnits"]

# Hand-built rather than captured: the documented nullable fields are set to null or left out,
# to show that a device or channel without them still parses.
GET_DEVICES_API_NULLS_RESPONSE = json.loads(
    """
{
  "generatedAt": "2026-11-04T04:43:49.806Z",
  "devices": [
    {
      "id": "12:34:56:78:90:AB",
      "serial": null,
      "lastSeen": null,
      "channels": [
        {
          "id": "1",
          "number": null,
          "enabled": true,
          "alarming": false,
          "probeFailed": false,
          "alarmHigh": null,
          "alarmLow": null,
          "minimum": null,
          "maximum": null,
          "lastTelemetrySaved": null
        }
      ]
    }
  ]
}"""
)

# Representative device responses informed by rparenton's captures in issue #46:
# https://github.com/a2hill/ha-thermoworks-cloud/issues/46#issuecomment-6633438207
# Keep one gateway and one meat probe independently, not the contributor's account layout.
# Only fields needed for these mapping contracts are retained; identifiers are placeholders.

GET_DEVICES_API_RFX_GATEWAY_RESPONSE = json.loads(
    """
{
  "generatedAt": "2026-11-04T14:12:14.228Z",
  "devices": [
    {
      "id": "test-rfx-gateway-id",
      "serial": "test-rfx-gateway-serial",
      "model": "rfx gateway",
      "displayUnits": "F",
      "type": "rfx",
      "fan": {
        "connected": true,
        "channel": "1",
        "setTemp": 275,
        "state": 1
      },
      "wifiSignal": -37,
      "gatewaySignal": null,
      "channels": [
        {
          "id": "1",
          "number": 1,
          "type": "Pro-Series",
          "value": 70.1999969482422,
          "units": "F"
        }
      ]
    }
  ]
}"""
)

GET_DEVICES_API_RFX_MEAT_RESPONSE = json.loads(
    """
{
  "generatedAt": "2026-11-04T14:12:14.228Z",
  "devices": [
    {
      "id": "test-rfx-meat-1-id",
      "serial": "test-rfx-meat-1-serial",
      "model": "rfx meat",
      "type": "rfx",
      "wifiSignal": null,
      "gatewaySignal": -66,
      "fan": null,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "type": "computed",
          "value": 69.7000045776367,
          "units": "F",
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z"
        },
        {
          "id": "1",
          "number": 1,
          "type": "rfx meat sensor",
          "value": 69.9000015258789,
          "units": "F",
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z"
        },
        {
          "id": "2",
          "number": 2,
          "type": "rfx meat sensor",
          "value": 69.9000015258789,
          "units": "F",
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z"
        },
        {
          "id": "3",
          "number": 3,
          "type": "rfx meat sensor",
          "value": 69.8000030517578,
          "units": "F",
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z"
        },
        {
          "id": "4",
          "number": 4,
          "type": "rfx meat sensor",
          "value": 69.7000045776367,
          "units": "F",
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z"
        }
      ]
    }
  ]
}"""
)


def _response_with_fan_state(state: Optional[int], connected: bool = True) -> DevicesResponse:
    """Vary fan state independently of probe count, channel values and other account details."""
    response = deepcopy(GET_DEVICES_API_RFX_GATEWAY_RESPONSE)
    fan = response["devices"][0]["fan"]
    fan["state"] = state
    fan["connected"] = connected
    return response


GET_DEVICES_API_BILLOWS_PAUSED_RESPONSE = _response_with_fan_state(FanState.PAUSED)
GET_DEVICES_API_BILLOWS_PULSING_RESPONSE = _response_with_fan_state(FanState.PULSING)
GET_DEVICES_API_BILLOWS_DISCONNECTED_RESPONSE = _response_with_fan_state(
    FanState.PAUSED, connected=False
)
# Synthetic combinations: connection and the last reported operating state are independent.
GET_DEVICES_API_BILLOWS_DISCONNECTED_BLOWING_RESPONSE = _response_with_fan_state(
    FanState.BLOWING, connected=False
)
GET_DEVICES_API_BILLOWS_DISCONNECTED_PULSING_RESPONSE = _response_with_fan_state(
    FanState.PULSING, connected=False
)
# Synthetic boundary cases: not observed states in the contributed captures.
GET_DEVICES_API_BILLOWS_UNKNOWN_RESPONSE = _response_with_fan_state(99)
GET_DEVICES_API_BILLOWS_NULL_STATE_RESPONSE = _response_with_fan_state(None)

def _response_with_channel_flag(*, flag: str, value: bool) -> DevicesResponse:
    """Vary one reported channel flag independently of the others."""
    response = deepcopy(GET_DEVICES_API_RESPONSE)
    response["devices"][0]["channels"][0][flag] = value
    return response


GET_DEVICES_API_DISABLED_CHANNEL_RESPONSE = _response_with_channel_flag(
    flag="enabled", value=False
)
GET_DEVICES_API_FAILED_PROBE_RESPONSE = _response_with_channel_flag(
    flag="probeFailed", value=True
)
GET_DEVICES_API_ALARMING_CHANNEL_RESPONSE = _response_with_channel_flag(
    flag="alarming", value=True
)
GET_DEVICES_API_MISSING_CHANNEL_FLAGS_RESPONSE = deepcopy(GET_DEVICES_API_RESPONSE)
for _flag in ("enabled", "probeFailed", "alarming"):
    del GET_DEVICES_API_MISSING_CHANNEL_FLAGS_RESPONSE["devices"][0]["channels"][0][_flag]

# Based on the NO PROBE channel excerpt in the issue below; remaining fields are representative.
# https://github.com/a2hill/ha-thermoworks-cloud/issues/46#issuecomment-6633350372
# A current device can retain a historical channel value despite reassuring boolean flags.
GET_DEVICES_API_NO_PROBE_RESPONSE = deepcopy(GET_DEVICES_API_RESPONSE)
GET_DEVICES_API_NO_PROBE_RESPONSE["devices"][0]["channels"][0].update({
    "status": "NO PROBE",
    "value": 76.8,
    "lastTelemetrySaved": "2026-09-09T12:49:36.000Z",
})

ERROR_RESPONSE = {"error": {"code": "invalid_api_key", "message": "Invalid API key"}}
