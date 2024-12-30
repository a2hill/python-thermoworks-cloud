"""Utility functions used within the library."""

from datetime import datetime

from aiohttp import ClientResponse


def parse_datetime(value: str) -> datetime:
    """Convert Firestore timestamp string to a datetime object."""
    return datetime.fromisoformat(value)


async def format_client_response(response: ClientResponse) -> str:
    """Format a string from the pertinent details of a response."""

    return f"status={response.status} reason={response.reason} body={await response.text()}"
