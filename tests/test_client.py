"""Tests of the API client's public interfaces."""

import pytest
from aiohttp import ClientError

from thermoworks_cloud import (
    ApiError,
    ApiAuthenticationError,
    MalformedResponseError,
    RateLimitError,
    ResourceNotFoundError,
)
from thermoworks_cloud.models import Account, ApiKeyInfo, Plan, RateLimit
from tests.test_data import (
    API_INVALID_DEVICES,
    API_INVALID_ACCOUNTS,
    API_NON_JSON_RESPONSES,
    API_INVALID_SNAPSHOT_RESPONSE,
    API_MAPPING_RESPONSE,
)


async def test_get_me(api_test_object):
    api_test_object.respond_me()
    account = await api_test_object.client.get_me()
    assert isinstance(account, Account)
    assert account.account_id == "account-1"
    assert isinstance(account.api_key, ApiKeyInfo)
    assert account.api_key.scopes == ["read:devices"]
    assert account.api_key.device_ids is None
    assert isinstance(account.plan, Plan)
    assert account.plan.api_tier == "free"
    assert isinstance(account.rate_limit, RateLimit)
    assert account.rate_limit.per_minute == 4
    assert account.recommended_poll_seconds == 60


async def test_get_devices(api_test_object):
    api_test_object.respond_devices()
    devices = await api_test_object.client.get_devices()
    assert len(devices) == 1
    assert devices[0].device_id == "device-1"
    assert devices[0].signal_strength == -55
    channels = api_test_object.client.get_device_channels("device-1")
    assert channels[0].number == "1"
    assert channels[0].value == 165.5
    assert channels[0].alarm_high.value == 200
    assert channels[0].alarm_high.units == "F"
    assert channels[0].additional_properties["id"] == "channel-1"
    assert channels[0].additional_properties["enabled"] is True


async def test_etag_uses_cached_snapshot(api_test_object):
    api_test_object.respond_unchanged()
    first = await api_test_object.client.get_devices()
    second = await api_test_object.client.get_devices()
    assert second == first
    assert api_test_object.client.get_device_channels("device-1")[0].value == 165.5


@pytest.mark.parametrize("status", [401, 403])
async def test_auth_errors(api_test_object, status):
    api_test_object.respond_error(status)
    with pytest.raises(ApiAuthenticationError):
        await api_test_object.client.get_devices()


async def test_rate_limit_exposes_delay(api_test_object):
    api_test_object.respond_rate_limited()
    with pytest.raises(RateLimitError) as error:
        await api_test_object.client.get_devices()
    assert error.value.retry_after == 12


async def test_rate_limit_http_date(api_test_object):
    api_test_object.respond_rate_limited_until_later()
    with pytest.raises(RateLimitError) as error:
        await api_test_object.client.get_devices()
    assert 0 < error.value.retry_after <= 60


async def test_missing_devices_array(api_test_object):
    api_test_object.respond_missing_devices()
    with pytest.raises(MalformedResponseError, match="devices array"):
        await api_test_object.client.get_devices()


@pytest.mark.parametrize("device", API_INVALID_DEVICES)
async def test_invalid_device_data(api_test_object, device):
    api_test_object.respond_invalid_device(device)
    with pytest.raises(MalformedResponseError):
        await api_test_object.client.get_devices()


async def test_uncached_304(api_test_object):
    api_test_object.expect_get_devices().respond_with_data(status=304)
    with pytest.raises(MalformedResponseError):
        await api_test_object.client.get_devices()


@pytest.mark.parametrize("status", [302, 401, 403, 429, 500])
async def test_error_body_cannot_expose_key(api_test_object, status):
    api_test_object.respond_error(status)
    with pytest.raises(ApiError) as error:
        await api_test_object.client.get_devices()
    assert api_test_object.key not in str(error.value)


@pytest.mark.parametrize("payload", API_INVALID_ACCOUNTS)
async def test_invalid_account_response(api_test_object, payload):
    api_test_object.expect_get_me().respond_with_json(payload)
    with pytest.raises(MalformedResponseError):
        await api_test_object.client.get_me()


@pytest.mark.parametrize("content_type, body", API_NON_JSON_RESPONSES)
async def test_invalid_json(api_test_object, content_type, body):
    api_test_object.expect_get_devices().respond_with_data(body, content_type=content_type)
    with pytest.raises(MalformedResponseError):
        await api_test_object.client.get_devices()


async def test_mapping_preserves_meaning(api_test_object):
    api_test_object.expect_get_devices().respond_with_json(API_MAPPING_RESPONSE)
    device = (await api_test_object.client.get_devices())[0]
    assert device.device_name is None
    assert device.type == "rfx"
    assert device.fan is None
    assert device.additional_properties["fan"] == API_MAPPING_RESPONSE["devices"][0]["fan"]
    channel = api_test_object.client.get_device_channels(device.device_id)[0]
    assert channel.number is None
    assert channel.additional_properties["id"] == "opaque-channel-id"
    assert channel.minimum.reading.value == 0
    assert channel.minimum.reading.units == "F"
    assert channel.minimum.date_reading is None
    assert channel.maximum.reading.value == 200
    assert channel.maximum.date_reading is None
    assert channel.last_seen.isoformat() == "2026-11-03T11:59:00+00:00"
    assert channel.last_telemetry_saved.isoformat() == "2026-11-03T11:58:30+00:00"


async def test_invalid_snapshot_does_not_replace_etag_or_cache(api_test_object):
    api_test_object.respond_devices()
    first = await api_test_object.client.get_devices()
    api_test_object.expect_get_devices('"snapshot-1"').respond_with_json(
        API_INVALID_SNAPSHOT_RESPONSE, headers={"ETag": '"snapshot-2"'}
    )
    with pytest.raises(MalformedResponseError):
        await api_test_object.client.get_devices()
    api_test_object.expect_get_devices('"snapshot-1"').respond_with_data(status=304)
    assert await api_test_object.client.get_devices() == first
    assert api_test_object.client.get_device_channels("device-1")[0].number == "1"


async def test_missing_device(api_test_object):
    api_test_object.respond_devices()
    with pytest.raises(ResourceNotFoundError):
        await api_test_object.client.get_device("missing")


@pytest.mark.parametrize("error_class", [ClientError, TimeoutError])
async def test_transport_errors_are_redacted(api_test_object, error_class):
    with api_test_object.fail_transport(error_class):
        with pytest.raises(ApiError) as error:
            await api_test_object.client.get_me()
    assert api_test_object.key not in str(error.value)
