"""Demonstrates how to use this library to get the devices visible to an API key.

This example shows how to:
1. Get all devices and their channels in a single request
2. Print detailed information about devices and their properties
3. Identify device-specific properties that may not be present in all device types
"""
import asyncio
import json
import os
import pprint
from dataclasses import asdict
from typing import Dict

from aiohttp import ClientSession

from thermoworks_cloud import ThermoworksClient
from thermoworks_cloud.models.device import Device

# Make sure this is defined
api_key = os.environ["THERMOWORKS_KEY"]

# This differs between cloud providers
BASE_URL = "https://cloud.thermoworks.com/api"


def print_device_info(device: Device):
    """Print detailed information about a device and its channels."""
    device_dict = asdict(device)
    device_channels = device.channels or []

    print(f"\n{'=' * 50}")
    print(f"DEVICE TYPE: {device.type or 'Unknown'}")
    print(f"DEVICE NAME: {device.label or 'Unnamed'}")
    print(f"SERIAL: {device.serial or 'Unknown'}")
    print(f"{'=' * 50}")

    # Print all device properties
    print("\nDEVICE PROPERTIES:")
    pprint.pprint(device_dict, compact=False)

    # Print channel information
    if device_channels:
        print(f"\nCHANNELS ({len(device_channels)}):")
        for i, channel in enumerate(device_channels):
            channel_dict = asdict(channel)
            print(f"\n  Channel {i+1}:")
            pprint.pprint(channel_dict)
    else:
        print("\nNo channels found for this device.")


async def __main__():
    # Use a context manager when providing the session to the client
    async with ClientSession() as session:
        thermoworks = ThermoworksClient(session, api_key, BASE_URL)
        devices = await thermoworks.get_devices()

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
            print_device_info(device)

        # Save the data to a JSON file for further analysis
        output_data = {"devices": [asdict(device) for device in devices]}

        with open("thermoworks_devices_data.json", "w", encoding="utf-8") as f:
            json.dump(output_data, f, indent=2, default=str)

        print("Data saved to thermoworks_devices_data.json for further analysis")


asyncio.run(__main__())
