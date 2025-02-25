"""Utility functions used within the library."""

from datetime import datetime

from aiohttp import ClientResponse


def parse_datetime(value: str) -> datetime:
    """Convert Firestore timestamp string to a datetime object."""
    return datetime.fromisoformat(value)


def unwrap_firestore_value(value_dict):
    """Unwrap a Firestore value dictionary into a single Python value.

    Args:
        value_dict (dict): A Firestore value dictionary containing a type and value

    Returns:
        The Python value
    """
    value = value_dict.values()
    if len(value) != 1:
        raise ValueError("Firestore values must contain a single value")
    return next(iter(value))


async def format_client_response(response: ClientResponse) -> str:
    """Format a string from the pertinent details of a response."""

    return f"status={response.status} reason={response.reason} body={await response.text()}"
