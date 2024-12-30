"""Test data to be used with mocks"""

import json

# Paths used by the AuthFactory to setup an authentication object
LOGIN_PATH = "/v1/accounts:signInWithPassword"
WEB_CONFIG_PATH = (
    "/v1alpha/projects/-/apps/1:78998049458:web:b41e9d405d8c7de95eefab/webConfig"
)
TOKEN_PATH = "/v1/token"

# Web facing API key for Firebase and Firestore attached to the requests by the AuthFactory
API_KEY = "AIzaSyCf079iccUFc1k7VHdGXng22zXDy8Y3KEY"
TEST_EMAIL_ADDRESS = "test@example.com"
TEST_PROJECT_ID = "test-project-id"
TEST_PASSWORD = "test_password"
TEST_USER_ID = "test_user_id"
TEST_ID_TOKEN = "test_id_token"
TEST_REFRESHED_ID_TOKEN = "test-refreshed-id-token"
TEST_REFRESH_TOKEN = "test_refresh_token"

# Root path used for application specific requests
FIREBASE_APPLICATION_BASE_PATH = (
    f"/v1/projects/{TEST_PROJECT_ID}/databases/(default)/documents"
)

# Return values from actual responses
LOGIN_RETURN_VALUE = {
    "idToken": TEST_ID_TOKEN,
    "email": TEST_EMAIL_ADDRESS,
    "refreshToken": TEST_REFRESH_TOKEN,
    "expiresIn": "3600",
    "localId": TEST_USER_ID,
}

# Actual response value structure
CONFIG_RETURN_VALUE = {
    "projectId": TEST_PROJECT_ID,
    "appId": "test-app-id",
    "databaseURL": "https://test-database-url.com",
    "storageBucket": "test-bucket.com",
    "locationId": "test-location-id",
    "authDomain": "test-auth-domain.com",
    "messagingSenderId": "test-message-sender-id",
    "measurementId": "test-measurement-id",
}

# Actual response value structure
TOKEN_REFRESH_RETURN_VALUE = {
    "access_token": TEST_REFRESHED_ID_TOKEN,
    "expires_in": "3600",
    "token_type": "Bearer",
    "refresh_token": "test-refreshed-refresh-token",
    "id_token": TEST_REFRESHED_ID_TOKEN,
    "user_id": TEST_USER_ID,
    "project_id": TEST_PROJECT_ID,
}

TEST_DEVICE_ID_0 = "12:34:56:78:90:AB"
TEST_DEVICE_ID_1 = "CD:EF:12:34:56:78"

# Actual response value structure
USER_RESPONSE = json.loads(
    """
{
  "name": "projects/test-project-name/databases/(default)/documents/users/test-user-id",
  "fields": {
    "system": {
      "mapValue": {
        "fields": {
          "hasPromptedEmailList": {
            "booleanValue": true
          }
        }
      }
    },
    "provider": {
      "stringValue": "firebase"
    },
    "deviceOrder": {
      "mapValue": {
        "fields": {
          "%s": {
            "arrayValue": {
              "values": [
                {
                  "mapValue": {
                    "fields": {
                      "deviceId": {
                        "stringValue": "%s"
                      },
                      "order": {
                        "integerValue": "0"
                      }
                    }
                  }
                },
                {
                  "mapValue": {
                    "fields": {
                      "deviceId": {
                        "stringValue": "%s"
                      },
                      "order": {
                        "integerValue": "1"
                      }
                    }
                  }
                }
              ]
            }
          }
        }
      }
    },
    "notificationSettings": {
      "mapValue": {
        "fields": {
          "emailNotification": {
            "booleanValue": false
          }
        }
      }
    },
    "timeZone": {
      "stringValue": "America/Los_Angeles"
    },
    "appVersion": {
      "stringValue": "1.61.6"
    },
    "displayName": {
      "stringValue": ""
    },
    "email": {
      "stringValue": "%s"
    },
    "exportVersion": {
      "doubleValue": 0.6
    },
    "use24Time": {
      "booleanValue": false
    },
    "emailStatus": {
      "stringValue": "bounce"
    },
    "fcmTokens": {
      "mapValue": {
        "fields": {
          "null": {
            "booleanValue": true
          },
          "token1": {
            "booleanValue": true
          },
          "token2": {
            "booleanValue": true
          }
        }
      }
    },
    "emailLastEvent": {
      "mapValue": {
        "fields": {
          "reason": {
            "stringValue": "Message queue continuously deferred for too long."
          },
          "event": {
            "stringValue": "bounce"
          },
          "email": {
            "stringValue": "%s"
          },
          "bounce_classification": {
            "stringValue": "Unclassified"
          },
          "tls": {
            "integerValue": "0"
          },
          "timestamp": {
            "integerValue": "1234567"
          },
          "smtp-id": {
            "stringValue": "\u003cmail@server.com\u003e"
          },
          "type": {
            "stringValue": "blocked"
          },
          "sg_message_id": {
            "stringValue": "12345.0987"
          },
          "sg_event_id": {
            "stringValue": "lkjhg12345"
          }
        }
      }
    },
    "accountId": {
      "stringValue": "test-account-id"
    },
    "uid": {
      "stringValue": "test-uid"
    },
    "roles": {
      "mapValue": {
        "fields": {
          "DataReader": {
            "booleanValue": true
          }
        }
      }
    },
    "lastSeenInApp": {
      "nullValue": null
    },
    "locale": {
      "stringValue": "en-US"
    },
    "photoURL": {
      "stringValue": ""
    },
    "accountRoles": {
      "mapValue": {
        "fields": {
          "accountAdmin": {
            "booleanValue": true
          }
        }
      }
    },
    "preferredUnits": {
      "stringValue": "F"
    },
    "lastLogin": {
      "timestampValue": "2020-01-01T00:00:00.000Z"
    }
  },
  "createTime": "2019-01-01T00:00:00.000Z",
  "updateTime": "2021-01-01T00:00:00.000Z"
}"""
    % (
        TEST_USER_ID,
        TEST_DEVICE_ID_0,
        TEST_DEVICE_ID_1,
        TEST_EMAIL_ADDRESS,
        TEST_EMAIL_ADDRESS,
    )
)

# Actual response value structure
GET_DEVICE_RESPONSE = json.loads(
    """
{
  "name": "projects/test-project-name/databases/(default)/documents/devices/%s",
  "fields": {
    "batteryState": {
      "stringValue": "discharging"
    },
    "bigQuery": {
      "mapValue": {
        "fields": {
          "tableId": {
            "stringValue": "%s"
          },
          "datasetId": {
            "stringValue": "test-dataset-id"
          }
        }
      }
    },
    "battery": {
      "integerValue": "100"
    },
    "lastArchive": {
      "timestampValue": "2021-01-01T00:00:00.000Z"
    },
    "status": {
      "stringValue": "NORMAL"
    },
    "lastWifiConnection": {
      "timestampValue": "2021-01-01T00:00:00.000Z"
    },
    "lastBluetoothConnection": {
      "timestampValue": "2021-01-01T00:00:00.000Z"
    },
    "type": {
      "stringValue": "datalogger"
    },
    "lastTelemetrySaved": {
      "timestampValue": "2021-01-01T00:00:00.000Z"
    },
    "pendingLoad": {
      "booleanValue": false
    },
    "exportVersion": {
      "doubleValue": 0.5
    },
    "sessionStart": {
      "timestampValue": "2021-01-01T00:00:00.000Z"
    },
    "deviceId": {
      "stringValue": "%s"
    },
    "serial": {
      "stringValue": "%s"
    },
    "transmitIntervalInSeconds": {
      "integerValue": "7200"
    },
    "deviceDisplayUnits": {
      "stringValue": "F"
    },
    "iotDeviceId": {
      "stringValue": "test-iot-device-id"
    },
    "label": {
      "stringValue": "NODE"
    },
    "lastPurged": {
      "timestampValue": "2021-01-01T00:00:00.000Z"
    },
    "batteryAlertSent": {
      "booleanValue": false
    },
    "color": {
      "stringValue": "3f90ca"
    },
    "firmware": {
      "stringValue": "1.0.26-26"
    },
    "thumbnail": {
      "stringValue": "node_bl.png"
    },
    "wifi_stength": {
      "integerValue": "-72"
    },
    "recordingIntervalInSeconds": {
      "integerValue": "600"
    },
    "accountId": {
      "stringValue": "test-account-id"
    },
    "lastSeen": {
      "timestampValue": "2021-01-01T00:00:00.000Z"
    },
    "device": {
      "stringValue": "node"
    }
  },
  "createTime": "2019-01-01T00:00:00.000Z",
  "updateTime": "2021-01-01T00:00:00.000Z"
}"""
    % (TEST_DEVICE_ID_0, TEST_DEVICE_ID_0, TEST_DEVICE_ID_0, TEST_DEVICE_ID_0)
)

# Actual response value structure
GET_DEVICE_CHANNEL_RESPONSE = json.loads(
    """
{
  "name": "projects/test-project-name/databases/(default)/documents/devices/test-device/channels/1",
  "fields": {
    "lastTelemetrySaved": {
      "timestampValue": "2021-01-01T00:00:00.000Z"
    },
    "value": {
      "doubleValue": -5.1999998092651367
    },
    "color": {
      "stringValue": "none"
    },
    "minimum": {
      "mapValue": {
        "fields": {
          "dateReading": {
            "timestampValue": "2021-01-01T00:00:00.000Z"
          },
          "reading": {
            "mapValue": {
              "fields": {
                "value": {
                  "doubleValue": -9.1000003814697266
                },
                "units": {
                  "stringValue": "F"
                }
              }
            }
          }
        }
      }
    },
    "units": {
      "stringValue": "F"
    },
    "status": {
      "stringValue": "NORMAL"
    },
    "type": {
      "stringValue": "test-device-channel-type"
    },
    "label": {
      "stringValue": "test-channel-label"
    },
    "lastSeen": {
      "timestampValue": "2021-01-01T00:00:00.000Z"
    },
    "alarmHigh": {
      "mapValue": {
        "fields": {
          "enabled": {
            "booleanValue": true
          },
          "units": {
            "stringValue": "F"
          },
          "alarming": {
            "booleanValue": false
          },
          "value": {
            "integerValue": "30"
          }
        }
      }
    },
    "number": {
      "stringValue": "test-channel-number"
    },
    "maximum": {
      "mapValue": {
        "fields": {
          "reading": {
            "mapValue": {
              "fields": {
                "value": {
                  "doubleValue": 69.5
                },
                "units": {
                  "stringValue": "F"
                }
              }
            }
          },
          "dateReading": {
            "timestampValue": "2021-01-01T00:00:00.000Z"
          }
        }
      }
    },
    "alarmLow": {
      "mapValue": {
        "fields": {
          "enabled": {
            "booleanValue": true
          },
          "units": {
            "stringValue": "F"
          },
          "alarming": {
            "booleanValue": false
          },
          "value": {
            "integerValue": "-12"
          }
        }
      }
    },
    "showAvgTemp": {
      "booleanValue": true
    }
  },
  "createTime": "2019-01-01T00:00:00.000Z",
  "updateTime": "2021-01-01T00:00:00.000Z"
}"""
)
