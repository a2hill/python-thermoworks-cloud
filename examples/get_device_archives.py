"""Demonstrates how to retrieve historical archives for a device.

This example shows how to:
1. List the available archive metadata for a device
2. Retrieve an archive using its filename
3. Iterate over the archived readings
"""

import asyncio
import os
from dataclasses import asdict
from pprint import pprint

from aiohttp import ClientSession

from thermoworks_cloud import AuthFactory, ThermoworksCloud

email = os.environ["THERMOWORKS_EMAIL"]
password = os.environ["THERMOWORKS_PASSWORD"]


async def __main__():
    async with ClientSession() as session:
        auth = await AuthFactory(session).build_auth(email, password)
        thermoworks = ThermoworksCloud(auth)

        user = await thermoworks.get_user()
        if not user.account_id:
            raise RuntimeError("No account ID found for user")

        devices = await thermoworks.get_devices(user.account_id)
        selected_serial = next(
            (device.serial for device in devices if device.serial), None
        )
        if selected_serial is None:
            raise RuntimeError("No device with a serial number found")

        archives = await thermoworks.list_device_archives(selected_serial)
        print(f"Found {len(archives)} archive(s) for device {selected_serial}")

        downloadable_archive = next(
            (archive for archive in archives if archive.filename), None
        )
        if downloadable_archive is None:
            print("No downloadable archives found.")
            return

        pprint(asdict(downloadable_archive))
        archive_data = await thermoworks.get_archive(downloadable_archive.filename)
        print(
            f"\nArchive contains {len(archive_data.readings)} reading(s) "
            f"from {archive_data.start} to {archive_data.end}"
        )

        for reading in archive_data.readings[:10]:
            print(
                reading.channel,
                reading.timestamp,
                reading.value,
                reading.units,
            )


asyncio.run(__main__())
