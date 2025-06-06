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


def parse_map_field(field_value: Dict, value_type: str) -> Optional[Dict]:
    """Parse a map field into a dictionary.

    Args:
        field_value: The Firestore field value containing a mapValue
        value_type: The type of values in the map (e.g., "booleanValue")

    Returns:
        A dictionary with the parsed values
    """
    if "mapValue" not in field_value or "fields" not in field_value["mapValue"]:
        return None

    result = {}
    for key, value in field_value["mapValue"]["fields"].items():
        if value_type in value:
            result[key] = value[value_type]

    return result


def map_firestore_fields(firestore_fields: Dict, dataclass_type: Type) -> Any:
    """Map Firestore fields to a dataclass instance based on field metadata.

    Args:
        firestore_fields: Dictionary containing Firestore fields
        dataclass_type: The dataclass type to map fields to

    Returns:
        An instance of the dataclass with fields populated from Firestore data
    """
    instance = dataclass_type()

    for field_info in dataclass_fields(dataclass_type):
        if field_info.name == 'additional_properties':
            continue

        # Get API field name
        api_name = api_field_name(field_info)

        # Skip if field is not in Firestore data
        if api_name not in firestore_fields:
            continue

        # Handle simple fields with firestore_type metadata
        if 'firestore_type' in field_info.metadata:
            firestore_type = field_info.metadata['firestore_type']
            converter = field_info.metadata.get('converter')

            # Set the field value
            value = get_field_value(
                firestore_fields, api_name, firestore_type, converter)
            setattr(instance, field_info.name, value)

        # Handle map fields with map_of metadata
        elif 'map_of' in field_info.metadata:
            value_type = field_info.metadata['map_of']
            value = parse_map_field(firestore_fields[api_name], value_type)
            setattr(instance, field_info.name, value)

    # Handle additional properties
    instance.additional_properties = extract_additional_properties(
        firestore_fields, dataclass_type)

    return instance


def parse_nested_object(data: dict, dataclass_type: Type) -> Any:
    """Parse a nested Firestore object into a dataclass instance.

    Args:
        data: The Firestore data containing a mapValue with fields
        dataclass_type: The dataclass type to map the fields to

    Returns:
        An instance of the dataclass type, or None if the data is invalid
    """
    if not data or "fields" not in data:
        return None

    return map_firestore_fields(data["fields"], dataclass_type)


async def format_client_response(response: ClientResponse) -> str:
    """Format a string from the pertinent details of a response."""
    return f"status={response.status} reason={response.reason} body={await response.text()}"
