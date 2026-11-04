"""Classes related to an Account."""

from dataclasses import dataclass
from typing import List, Optional, TypedDict


class _ApiKeyResponse(TypedDict, total=False):
    """The `apiKey` object in a response from the `/v1/me` API."""

    id: str
    name: str
    scopes: List[str]
    deviceIds: Optional[List[str]]


class _PlanResponse(TypedDict, total=False):
    """The `plan` object in a response from the `/v1/me` API."""

    id: Optional[str]
    apiTier: str


class _RateLimitResponse(TypedDict, total=False):
    """The `rateLimit` object in a response from the `/v1/me` API."""

    perMinute: int
    perDay: int


class _AccountResponse(TypedDict, total=False):
    """A response from the `/v1/me` API."""

    accountId: str
    apiKey: _ApiKeyResponse
    plan: _PlanResponse
    rateLimit: _RateLimitResponse
    recommendedPollSeconds: int


@dataclass
class ApiKeyInfo:
    """ApiKeyInfo contains metadata about an API key. It never contains the key itself."""

    id: Optional[str] = None
    name: Optional[str] = None
    scopes: Optional[List[str]] = None
    device_ids: Optional[List[str]] = None


@dataclass
class Plan:
    """Plan contains information about an account's plan."""

    id: Optional[str] = None
    api_tier: Optional[str] = None


@dataclass
class RateLimit:
    """RateLimit contains the number of requests an API key can make."""

    per_minute: Optional[int] = None
    per_day: Optional[int] = None


@dataclass
class Account:
    """Account contains information about the account an API key belongs to."""

    account_id: Optional[str] = None
    api_key: Optional[ApiKeyInfo] = None
    plan: Optional[Plan] = None
    rate_limit: Optional[RateLimit] = None
    recommended_poll_seconds: Optional[int] = None


def _json_to_account(data: _AccountResponse) -> Account:
    """Convert a response from the `/v1/me` API into an Account object."""
    api_key = data.get("apiKey")
    plan = data.get("plan")
    rate_limit = data.get("rateLimit")

    return Account(
        account_id=data.get("accountId"),
        api_key=ApiKeyInfo(
            id=api_key.get("id"),
            name=api_key.get("name"),
            scopes=api_key.get("scopes"),
            device_ids=api_key.get("deviceIds"),
        ) if api_key else None,
        plan=Plan(id=plan.get("id"), api_tier=plan.get("apiTier")) if plan else None,
        rate_limit=RateLimit(
            per_minute=rate_limit.get("perMinute"),
            per_day=rate_limit.get("perDay"),
        ) if rate_limit else None,
        recommended_poll_seconds=data.get("recommendedPollSeconds"),
    )
