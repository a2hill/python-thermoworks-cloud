"""Account and API-key metadata returned by the API's /me endpoint."""

from dataclasses import dataclass

from thermoworks_cloud.utils import _object, _field


@dataclass
class ApiKeyInfo:
    """Metadata about a key, excluding its secret value."""

    id: str | None = None
    name: str | None = None
    scopes: list[str] | None = None
    device_ids: list[str] | None = None


@dataclass
class Plan:
    """Account plan and API access tier."""

    id: str | None = None
    api_tier: str | None = None


@dataclass
class RateLimit:
    """Request budgets advertised by the service."""

    per_minute: int | None = None
    per_day: int | None = None


@dataclass
class Account:
    """API account metadata; distinct from a Firebase user profile."""

    account_id: str
    api_key: ApiKeyInfo | None = None
    plan: Plan | None = None
    rate_limit: RateLimit | None = None
    recommended_poll_seconds: int | None = None


def _strings(data: dict, name: str) -> list[str] | None:
    value = _field(data, name, list)
    if value is not None and any(not isinstance(item, str) for item in value):
        raise ValueError(f"Invalid API field: {name}")
    return value


def _api_to_account(payload: dict) -> Account:
    """Convert /me JSON using the same model-converter boundary as Firebase."""
    data = _object(payload)
    account = Account(
        account_id=_field(data, "accountId", str, required=True),
        recommended_poll_seconds=_field(data, "recommendedPollSeconds", int),
    )
    if data.get("apiKey") is not None:
        key = _object(data["apiKey"])
        account.api_key = ApiKeyInfo(
            id=_field(key, "id", str),
            name=_field(key, "name", str),
            scopes=_strings(key, "scopes"),
            device_ids=_strings(key, "deviceIds"),
        )
    if data.get("plan") is not None:
        plan = _object(data["plan"])
        account.plan = Plan(id=_field(plan, "id", str), api_tier=_field(plan, "apiTier", str))
    if data.get("rateLimit") is not None:
        limits = _object(data["rateLimit"])
        account.rate_limit = RateLimit(
            per_minute=_field(limits, "perMinute", int), per_day=_field(limits, "perDay", int)
        )
    return account
