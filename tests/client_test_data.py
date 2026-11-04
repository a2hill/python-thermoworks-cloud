"""Test data for the ThermoworksClient tests."""

from copy import deepcopy
import json

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

# Hand-built from the captured response above, for a device reporting through a gateway with a
# connected fan. Neither has been captured, so the values are invented and the fan's field names
# are assumed to match Firebase, see
# GET_DEVICE_WITH_FAN_RESPONSE in test_data.py.
GET_DEVICES_API_WITH_GATEWAY_AND_FAN_RESPONSE = deepcopy(GET_DEVICES_API_RESPONSE)
GET_DEVICES_API_WITH_GATEWAY_AND_FAN_RESPONSE["devices"][0].update({
    "gatewaySignal": -55,
    "fan": {
        "connected": True,
        "connection": True,
        "fan_channel": "1",
        "setTemp": 150,
        "state": 1,
    },
})

ERROR_RESPONSE = {"error": {"code": "invalid_api_key", "message": "Invalid API key"}}
