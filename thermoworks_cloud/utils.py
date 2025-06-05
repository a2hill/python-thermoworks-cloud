"""Utility functions used within the library."""

from dataclasses import Field, fields as dataclass_fields
from datetime import datetime
from typing import Any, Callable, Dict, Optional, Type

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


def api_field_name(field: Field) -> str:
    """Get the API field name for a dataclass field.

    Checks for a 'api_name' metadata entry, otherwise converts from snake_case to camelCase.

    Args:
        field: A dataclass field

    Returns:
        The API field name
    """
    # Check if the field has an api_name metadata entry
    if 'api_name' in field.metadata:
        return field.metadata['api_name']

    # Otherwise convert from snake_case to camelCase
    parts = field.name.split('_')
    return parts[0] + ''.join(p.capitalize() for p in parts[1:])


def extract_additional_properties(firestore_fields: Dict, dataclass_type: Type) -> Optional[Dict]:
    """Extract additional properties not explicitly mapped.

    Args:
        firestore_fields: Dictionary containing Firestore fields
        dataclass_type: The dataclass type to extract field names from

    Returns:
        Dictionary of additional properties, or None if none found
    """
    # Generate known fields from dataclass
    known_fields = set()
    for field in dataclass_fields(dataclass_type):
        if field.name == 'additional_properties':
            continue

        # Get the API field name
        known_fields.add(api_field_name(field))

    # Extract additional properties
    additional_props = {}
    for field_name, field_value in firestore_fields.items():
        if field_name not in known_fields:
            # Store the raw value for additional properties
            value_type = next(iter(field_value.keys()))
            additional_props[field_name] = field_value[value_type]

    return additional_props if additional_props else None


async def format_client_response(response: ClientResponse) -> str:
    """Format a string from the pertinent details of a response."""
    return f"status={response.status} reason={response.reason} body={await response.text()}"