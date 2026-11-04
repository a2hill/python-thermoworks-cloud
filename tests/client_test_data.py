"""Test data for the ThermoworksClient tests."""

# Keep the contributed responses complete, including every physical and computed channel.
# pylint: disable=too-many-lines

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

# Captured by rparenton in ha-thermoworks-cloud issue #46:
# https://github.com/a2hill/ha-thermoworks-cloud/issues/46#issuecomment-6633438207
# Only device id/serial placeholders are changed: every source device used "redacted".
# Distinct, stable placeholders identify each gateway/probe across captures. The source does
# not establish whether an original device's id and serial were equal.

# Source: https://github.com/user-attachments/files/34377190/RFX_No_Billows.txt
GET_DEVICES_API_RFX_BILLOWS_DISCONNECTED_RESPONSE = json.loads(
    """
{
  "generatedAt": "2026-11-04T14:19:49.848Z",
  "devices": [
    {
      "id": "test-rfx-gateway-id",
      "serial": "test-rfx-gateway-serial",
      "label": "RFX Gateway",
      "model": "rfx gateway",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": "1.2.3-47",
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": {
        "connected": false,
        "channel": "1",
        "setTemp": 275,
        "state": 0
      },
      "wifiSignal": -37,
      "gatewaySignal": null,
      "lastSeen": "2026-11-04T14:19:37.260Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 30,
      "channels": [
        {
          "id": "1",
          "number": 1,
          "label": "Grid Temperature",
          "type": "Pro-Series",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 250,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 200,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 289.79998779296875,
          "lastTelemetrySaved": "2026-11-04T14:19:36.503Z",
          "lastSeen": "2026-11-04T14:19:37.260Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-1-id",
      "serial": "test-rfx-meat-1-serial",
      "label": "Meat Probe 1",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -69,
      "lastSeen": "2026-11-04T14:16:55.613Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 69.89999389648438,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:16:55.414Z",
          "lastSeen": "2026-11-04T14:16:55.613Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.1999969482422,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.1999969482422,
          "lastTelemetrySaved": "2026-11-04T14:16:55.414Z",
          "lastSeen": "2026-11-04T14:16:55.613Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:16:55.414Z",
          "lastSeen": "2026-11-04T14:16:55.613Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.7000045776367,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:16:55.414Z",
          "lastSeen": "2026-11-04T14:16:55.613Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.89999389648438,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:16:55.414Z",
          "lastSeen": "2026-11-04T14:16:55.613Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-2-id",
      "serial": "test-rfx-meat-2-serial",
      "label": "Meat Probe 2",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -69,
      "lastSeen": "2026-11-04T14:16:59.437Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 133,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.6999969482422,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:16:59.214Z",
          "lastSeen": "2026-11-04T14:16:59.437Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.3000030517578,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.3000030517578,
          "lastTelemetrySaved": "2026-11-04T14:16:59.214Z",
          "lastSeen": "2026-11-04T14:16:59.437Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.6999969482422,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:16:59.214Z",
          "lastSeen": "2026-11-04T14:16:59.437Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.10000610351562,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.10000610351562,
          "lastTelemetrySaved": "2026-11-04T14:16:59.214Z",
          "lastSeen": "2026-11-04T14:16:59.437Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.10000610351562,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.7999954223633,
          "maximum": 70.10000610351562,
          "lastTelemetrySaved": "2026-11-04T14:16:59.214Z",
          "lastSeen": "2026-11-04T14:16:59.437Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-3-id",
      "serial": "test-rfx-meat-3-serial",
      "label": "Meat Probe 3",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -72,
      "lastSeen": "2026-11-04T14:17:02.297Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.1999969482422,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:17:02.125Z",
          "lastSeen": "2026-11-04T14:17:02.297Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.1999969482422,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:17:02.125Z",
          "lastSeen": "2026-11-04T14:17:02.297Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.39999389648438,
          "maximum": 70.5999984741211,
          "lastTelemetrySaved": "2026-11-04T14:17:02.125Z",
          "lastSeen": "2026-11-04T14:17:02.297Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.8000030517578,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.5,
          "maximum": 70.8000030517578,
          "lastTelemetrySaved": "2026-11-04T14:17:02.125Z",
          "lastSeen": "2026-11-04T14:17:02.297Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.2999954223633,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:17:02.125Z",
          "lastSeen": "2026-11-04T14:17:02.297Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-4-id",
      "serial": "test-rfx-meat-4-serial",
      "label": "Meat Probe 4",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -67,
      "lastSeen": "2026-11-04T14:17:03.439Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:17:03.254Z",
          "lastSeen": "2026-11-04T14:17:03.439Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.1999969482422,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.1999969482422,
          "lastTelemetrySaved": "2026-11-04T14:17:03.254Z",
          "lastSeen": "2026-11-04T14:17:03.439Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.1999969482422,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.1999969482422,
          "lastTelemetrySaved": "2026-11-04T14:17:03.254Z",
          "lastSeen": "2026-11-04T14:17:03.439Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:17:03.254Z",
          "lastSeen": "2026-11-04T14:17:03.439Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.9000015258789,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:17:03.254Z",
          "lastSeen": "2026-11-04T14:17:03.439Z"
        }
      ]
    }
  ]
}"""
)

# Source: https://github.com/user-attachments/files/34377189/RFX_with_Billows_Blowing.txt
GET_DEVICES_API_RFX_BILLOWS_BLOWING_RESPONSE = json.loads(
    """
{
  "generatedAt": "2026-11-04T14:12:14.228Z",
  "devices": [
    {
      "id": "test-rfx-gateway-id",
      "serial": "test-rfx-gateway-serial",
      "label": "RFX Gateway",
      "model": "rfx gateway",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": "1.2.3-47",
      "locationId": null,
      "battery": 100,
      "batteryState": "charging",
      "fan": {
        "connected": true,
        "channel": "1",
        "setTemp": 275,
        "state": 1
      },
      "wifiSignal": -37,
      "gatewaySignal": null,
      "lastSeen": "2026-11-04T14:12:07.246Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 30,
      "channels": [
        {
          "id": "1",
          "number": 1,
          "label": "Grid Temperature",
          "type": "Pro-Series",
          "enabled": true,
          "value": 70.1999969482422,
          "units": "F",
          "status": "LOW",
          "probeFailed": false,
          "alarming": true,
          "alarmHigh": {
            "enabled": true,
            "value": 300,
            "alarming": false
          },
          "alarmLow": {
            "enabled": true,
            "value": 250,
            "alarming": true
          },
          "minimum": 70.1999969482422,
          "maximum": 289.79998779296875,
          "lastTelemetrySaved": "2026-11-04T14:12:06.502Z",
          "lastSeen": "2026-11-04T14:12:07.246Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-1-id",
      "serial": "test-rfx-meat-1-serial",
      "label": "Meat Probe 1",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -66,
      "lastSeen": "2026-11-04T14:10:55.326Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 69.7000045776367,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 69.7000045776367,
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z",
          "lastSeen": "2026-11-04T14:10:55.326Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.9000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z",
          "lastSeen": "2026-11-04T14:10:55.326Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.9000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z",
          "lastSeen": "2026-11-04T14:10:55.326Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.8000030517578,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.7000045776367,
          "maximum": 69.8000030517578,
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z",
          "lastSeen": "2026-11-04T14:10:55.326Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.7000045776367,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 69.7000045776367,
          "lastTelemetrySaved": "2026-11-04T14:10:55.122Z",
          "lastSeen": "2026-11-04T14:10:55.326Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-2-id",
      "serial": "test-rfx-meat-2-serial",
      "label": "Meat Probe 2",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -69,
      "lastSeen": "2026-11-04T14:10:59.094Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 69.7999954223633,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 133,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.6999969482422,
          "maximum": 69.8000030517578,
          "lastTelemetrySaved": "2026-11-04T14:10:58.924Z",
          "lastSeen": "2026-11-04T14:10:59.094Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:10:58.924Z",
          "lastSeen": "2026-11-04T14:10:59.094Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.7999954223633,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.6999969482422,
          "maximum": 69.8000030517578,
          "lastTelemetrySaved": "2026-11-04T14:10:58.924Z",
          "lastSeen": "2026-11-04T14:10:59.094Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.9000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:10:58.924Z",
          "lastSeen": "2026-11-04T14:10:59.094Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.7999954223633,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.7999954223633,
          "maximum": 69.8000030517578,
          "lastTelemetrySaved": "2026-11-04T14:10:58.924Z",
          "lastSeen": "2026-11-04T14:10:59.094Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-3-id",
      "serial": "test-rfx-meat-3-serial",
      "label": "Meat Probe 3",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -67,
      "lastSeen": "2026-11-04T14:11:02.004Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 70.4000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.1999969482422,
          "maximum": 70.4000015258789,
          "lastTelemetrySaved": "2026-11-04T14:11:01.833Z",
          "lastSeen": "2026-11-04T14:11:02.004Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.4000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.1999969482422,
          "maximum": 70.4000015258789,
          "lastTelemetrySaved": "2026-11-04T14:11:01.833Z",
          "lastSeen": "2026-11-04T14:11:02.004Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.4000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.39999389648438,
          "maximum": 70.4000015258789,
          "lastTelemetrySaved": "2026-11-04T14:11:01.833Z",
          "lastSeen": "2026-11-04T14:11:02.004Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.5,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:11:01.833Z",
          "lastSeen": "2026-11-04T14:11:02.004Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.4000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.2999954223633,
          "maximum": 70.4000015258789,
          "lastTelemetrySaved": "2026-11-04T14:11:01.833Z",
          "lastSeen": "2026-11-04T14:11:02.004Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-4-id",
      "serial": "test-rfx-meat-4-serial",
      "label": "Meat Probe 4",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -64,
      "lastSeen": "2026-11-04T14:11:03.180Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 69.9000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:11:02.973Z",
          "lastSeen": "2026-11-04T14:11:03.180Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:11:02.973Z",
          "lastSeen": "2026-11-04T14:11:03.180Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:11:02.973Z",
          "lastSeen": "2026-11-04T14:11:03.180Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:11:02.973Z",
          "lastSeen": "2026-11-04T14:11:03.180Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.9000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.9000015258789,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:11:02.973Z",
          "lastSeen": "2026-11-04T14:11:03.180Z"
        }
      ]
    }
  ]
}"""
)

# Source: https://github.com/user-attachments/files/34377191/RFX_with_Billows_Paused.txt
GET_DEVICES_API_RFX_BILLOWS_PAUSED_RESPONSE = json.loads(
    """
{
  "generatedAt": "2026-11-04T14:14:18.485Z",
  "devices": [
    {
      "id": "test-rfx-gateway-id",
      "serial": "test-rfx-gateway-serial",
      "label": "RFX Gateway",
      "model": "rfx gateway",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": "1.2.3-47",
      "locationId": null,
      "battery": 100,
      "batteryState": "charging",
      "fan": {
        "connected": true,
        "channel": "1",
        "setTemp": 50,
        "state": 0
      },
      "wifiSignal": -37,
      "gatewaySignal": null,
      "lastSeen": "2026-11-04T14:14:07.206Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 30,
      "channels": [
        {
          "id": "1",
          "number": 1,
          "label": "Grid Temperature",
          "type": "Pro-Series",
          "enabled": true,
          "value": 69.8000030517578,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": true,
            "value": 75,
            "alarming": false
          },
          "alarmLow": {
            "enabled": true,
            "value": 25,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 289.79998779296875,
          "lastTelemetrySaved": "2026-11-04T14:14:06.502Z",
          "lastSeen": "2026-11-04T14:14:07.206Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-1-id",
      "serial": "test-rfx-meat-1-serial",
      "label": "Meat Probe 1",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -69,
      "lastSeen": "2026-11-04T14:13:55.461Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 69.9000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.7000045776367,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.9000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-2-id",
      "serial": "test-rfx-meat-2-serial",
      "label": "Meat Probe 2",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -68,
      "lastSeen": "2026-11-04T14:13:59.317Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 69.89999389648438,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 133,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.6999969482422,
          "maximum": 69.89999389648438,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.1999969482422,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.1999969482422,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.89999389648438,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.6999969482422,
          "maximum": 69.89999389648438,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.7999954223633,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-3-id",
      "serial": "test-rfx-meat-3-serial",
      "label": "Meat Probe 3",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -72,
      "lastSeen": "2026-11-04T14:14:02.216Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.1999969482422,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.1999969482422,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.39999389648438,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.5,
          "maximum": 70.5999984741211,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.2999954223633,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-4-id",
      "serial": "test-rfx-meat-4-serial",
      "label": "Meat Probe 4",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -68,
      "lastSeen": "2026-11-04T14:14:03.307Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.1999969482422,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.1999969482422,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.9000015258789,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        }
      ]
    }
  ]
}"""
)

# Source: https://github.com/user-attachments/files/34377192/RFX_with_Billows_Pulsing.txt
GET_DEVICES_API_RFX_BILLOWS_PULSING_RESPONSE = json.loads(
    """
{
  "generatedAt": "2026-11-04T14:16:13.331Z",
  "devices": [
    {
      "id": "test-rfx-gateway-id",
      "serial": "test-rfx-gateway-serial",
      "label": "RFX Gateway",
      "model": "rfx gateway",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": "1.2.3-47",
      "locationId": null,
      "battery": 100,
      "batteryState": "charging",
      "fan": {
        "connected": true,
        "channel": "1",
        "setTemp": 70,
        "state": 2
      },
      "wifiSignal": -37,
      "gatewaySignal": null,
      "lastSeen": "2026-11-04T14:16:07.231Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 30,
      "channels": [
        {
          "id": "1",
          "number": 1,
          "label": "Grid Temperature",
          "type": "Pro-Series",
          "enabled": true,
          "value": 69.5999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": true,
            "value": 95,
            "alarming": false
          },
          "alarmLow": {
            "enabled": true,
            "value": 45,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 289.79998779296875,
          "lastTelemetrySaved": "2026-11-04T14:16:06.502Z",
          "lastSeen": "2026-11-04T14:16:07.231Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-1-id",
      "serial": "test-rfx-meat-1-serial",
      "label": "Meat Probe 1",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -69,
      "lastSeen": "2026-11-04T14:13:55.461Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 69.9000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.7000045776367,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.9000015258789,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.5999984741211,
          "maximum": 69.9000015258789,
          "lastTelemetrySaved": "2026-11-04T14:13:55.294Z",
          "lastSeen": "2026-11-04T14:13:55.461Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-2-id",
      "serial": "test-rfx-meat-2-serial",
      "label": "Meat Probe 2",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -68,
      "lastSeen": "2026-11-04T14:13:59.317Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 69.89999389648438,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 133,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.6999969482422,
          "maximum": 69.89999389648438,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.1999969482422,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.1999969482422,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 69.89999389648438,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.6999969482422,
          "maximum": 69.89999389648438,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.7999954223633,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:13:59.094Z",
          "lastSeen": "2026-11-04T14:13:59.317Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-3-id",
      "serial": "test-rfx-meat-3-serial",
      "label": "Meat Probe 3",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -72,
      "lastSeen": "2026-11-04T14:14:02.216Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.1999969482422,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.1999969482422,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.39999389648438,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.5,
          "maximum": 70.5999984741211,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.5,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70.2999954223633,
          "maximum": 70.5,
          "lastTelemetrySaved": "2026-11-04T14:14:02.004Z",
          "lastSeen": "2026-11-04T14:14:02.216Z"
        }
      ]
    },
    {
      "id": "test-rfx-meat-4-id",
      "serial": "test-rfx-meat-4-serial",
      "label": "Meat Probe 4",
      "model": "rfx meat",
      "displayUnits": "F",
      "type": "rfx",
      "firmware": null,
      "locationId": null,
      "battery": 100,
      "batteryState": "discharging",
      "fan": null,
      "wifiSignal": null,
      "gatewaySignal": -68,
      "lastSeen": "2026-11-04T14:14:03.307Z",
      "nextExpectedConnection": null,
      "transmitIntervalSeconds": 60,
      "channels": [
        {
          "id": "0",
          "number": 0,
          "label": "Temperature",
          "type": "computed",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 203,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        },
        {
          "id": "1",
          "number": 1,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.0999984741211,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.0999984741211,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        },
        {
          "id": "2",
          "number": 2,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70.1999969482422,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 70,
          "maximum": 70.1999969482422,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        },
        {
          "id": "3",
          "number": 3,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.8000030517578,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        },
        {
          "id": "4",
          "number": 4,
          "label": null,
          "type": "rfx meat sensor",
          "enabled": true,
          "value": 70,
          "units": "F",
          "status": "NORMAL",
          "probeFailed": false,
          "alarming": false,
          "alarmHigh": {
            "enabled": false,
            "value": 165,
            "alarming": false
          },
          "alarmLow": {
            "enabled": false,
            "value": 32,
            "alarming": false
          },
          "minimum": 69.9000015258789,
          "maximum": 70,
          "lastTelemetrySaved": "2026-11-04T14:14:03.144Z",
          "lastSeen": "2026-11-04T14:14:03.307Z"
        }
      ]
    }
  ]
}"""
)

ERROR_RESPONSE = {"error": {"code": "invalid_api_key", "message": "Invalid API key"}}
