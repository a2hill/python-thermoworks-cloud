"""Demonstrates how to use this library to get the devices for the logged in user."""

import asyncio
import os
from aiohttp import ClientSession

from thermoworks_cloud import AuthFactory, ThermoworksCloud, ResourceNotFoundError
from thermoworks_cloud.models.device import Device
from thermoworks_cloud.models.device_channel import DeviceChannel

# Make sure these are defined
email = os.environ["THERMOWORKS_EMAIL"]
password = os.environ["THERMOWORKS_PASSWORD"]


async def __main__():
    # User a context manager when providing the session to the auth factory
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
            for device_order_item in user.device_order[user.account_id]
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

        assert len(devices) > 0
        assert len(device_channels_by_device[devices[0].serial]) > 0

        print({
            "devices": devices,
            "device_channels": device_channels_by_device,
        })


asyncio.run(__main__())
