"""Utility functions used within the library."""

from datetime import datetime
from typing import Any, Callable, Dict, Optional

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


def get_field_value(fields: Dict, field_name: str, value_type: str,
                    converter: Optional[Callable] = None) -> Any:
    """Helper function to safely get values from Firestore fields.

    Args:
        fields: Dictionary containing Firestore fields
        field_name: Name of the field to retrieve
        value_type: Type of value to retrieve (e.g., "stringValue", "integerValue")
        converter: Optional function to convert the value

    Returns:
        The value if found, or None if not found
    """
    if field_name in fields and value_type in fields[field_name]:
        value = fields[field_name][value_type]
        return converter(value) if converter else value
    return None


def extract_additional_properties(fields: Dict, known_fields: set) -> Optional[Dict]:
    """Extract additional properties not explicitly mapped.

    Args:
        fields: Dictionary containing Firestore fields
        known_fields: Set of field names that are already handled

    Returns:
        Dictionary of additional properties, or None if none found
    """
    additional_props = {}

    for field_name, field_value in fields.items():
        if field_name not in known_fields:
            # Store the raw value for additional properties
            value_type = next(iter(field_value.keys()))
            additional_props[field_name] = field_value[value_type]

    return additional_props if additional_props else None


async def format_client_response(response: ClientResponse) -> str:
    """Format a string from the pertinent details of a response."""
    return f"status={response.status} reason={response.reason} body={await response.text()}"
