"""Demonstrates how to use this library to get the devices for the logged in user.

This example shows how to:
1. Get all devices for a user
2. Get all channels for each device
3. Print detailed information about devices and their properties
4. Identify device-specific properties that may not be present in all device types
"""
import asyncio
import json
import os
import pprint
from dataclasses import asdict
from typing import Dict

from aiohttp import ClientSession

from thermoworks_cloud import AuthFactory, ThermoworksCloud, ResourceNotFoundError
from thermoworks_cloud.models.device import Device
from thermoworks_cloud.models.device_channel import DeviceChannel

# Make sure these are defined
email = os.environ["THERMOWORKS_EMAIL"]
password = os.environ["THERMOWORKS_PASSWORD"]


def dataclass_to_dict(obj):
    """Convert a dataclass instance to a dictionary, handling None values and nested dataclasses."""
    if obj is None:
        return None

    if hasattr(obj, "__dataclass_fields__"):
        result = {}
        for key, value in asdict(obj).items():
            if key == "additional_properties" and value is not None:
                # Merge additional properties into the main dictionary
                result.update(value)
            elif value is not None:  # Skip None values for cleaner output
                if isinstance(value, dict):
                    result[key] = dataclass_to_dict(value)
                else:
                    result[key] = value
        return result
    elif isinstance(obj, dict):
        return {k: dataclass_to_dict(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [dataclass_to_dict(item) for item in obj]
    else:
        return obj


def print_device_info(device: Device, device_channels: list[DeviceChannel]):
    """Print detailed information about a device and its channels."""
    device_dict = dataclass_to_dict(device)

    print(f"\n{'=' * 50}")
    print(f"DEVICE TYPE: {device.type or 'Unknown'}")
    print(f"DEVICE NAME: {device.label or 'Unnamed'}")
    print(f"SERIAL: {device.serial or 'Unknown'}")
    print(f"{'=' * 50}")

    # Print all device properties
    print("\nDEVICE PROPERTIES:")
    pprint.pprint(device_dict)

    # Print channel information
    if device_channels:
        print(f"\nCHANNELS ({len(device_channels)}):")
        for i, channel in enumerate(device_channels):
            channel_dict = dataclass_to_dict(channel)
            print(f"\n  Channel {i+1}:")
            pprint.pprint(channel_dict)
    else:
        print("\nNo channels found for this device.")


async def __main__():
    # Use a context manager when providing the session to the auth factory
    async with ClientSession() as session:
        auth = await AuthFactory(session).build_auth(email, password)
        thermoworks = ThermoworksCloud(auth)
        user = await thermoworks.get_user()

        # To store the devices we find
        devices: list[Device] = []
        device_channels_by_device: dict[str, list[DeviceChannel]] = {}

        # Get the device serial numbers from the user document
        device_serials = [
            device_order_item.device_id
            for device_order_item in user.device_order.get(user.account_id, [])
        ]

        # Iterate over the device serials and fetch the device document for each
        for device_serial in device_serials:
            device = await thermoworks.get_device(device_serial)
            devices.append(device)
            device_channels = []

            # According to reverse engineering, channels seem to be 1 indexed
            for channel in range(1, 10):
                try:
                    device_channels.append(
                        await thermoworks.get_device_channel(
                            device_serial=device_serial, channel=str(channel)
                        )
                    )
                except ResourceNotFoundError:
                    # Go until there are no more
                    break

            device_channels_by_device[device_serial] = device_channels

        # Print information about each device
        print(f"\nFound {len(devices)} devices")

        # Group devices by type
        devices_by_type: Dict[str, list[Device]] = {}
        for device in devices:
            device_type = device.type or "unknown"
            if device_type not in devices_by_type:
                devices_by_type[device_type] = []
            devices_by_type[device_type].append(device)

        # Print summary of device types
        print("\nDEVICE TYPES SUMMARY:")
        for device_type, type_devices in devices_by_type.items():
            print(f"  {device_type}: {len(type_devices)} device(s)")

        # Print detailed information for each device
        for device in devices:
            device_channels = device_channels_by_device.get(device.serial, [])
            print_device_info(device, device_channels)

        # Save the data to a JSON file for further analysis
        output_data = {
            "devices": [dataclass_to_dict(device) for device in devices],
            "device_channels": {
                serial: [dataclass_to_dict(channel) for channel in channels]
                for serial, channels in device_channels_by_device.items()
            }
        }

        with open("thermoworks_devices_data.json", "w") as f:
            json.dump(output_data, f, indent=2, default=str)

        print(f"\nData saved to thermoworks_devices_data.json for further analysis")


asyncio.run(__main__())
