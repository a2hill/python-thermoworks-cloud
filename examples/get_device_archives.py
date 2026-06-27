"""Demonstrates how to retrieve historical archives for a device.

This example shows how to:
1. List every page of archive metadata, newest first
2. Pass each page token to retrieve the next page
3. Retrieve the most recent archive using its filename
4. Iterate over the archived readings
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

        page_token = None
        page_number = 0
        archive_count = 0
        latest_archive = None

        while True:
            archive_page = await thermoworks.list_device_archives(
                selected_serial,
                page_token=page_token,
                order="desc",
            )
            page_number += 1
            archive_count += len(archive_page.archives)

            if latest_archive is None and archive_page.archives:
                latest_archive = archive_page.archives[0]

            print(
                f"Fetched page {page_number} with {len(archive_page.archives)} "
                f"archive(s); another page: {bool(archive_page.next_page_token)}"
            )

            page_token = archive_page.next_page_token
            if not page_token:
                break

        print(f"Found {archive_count} archive(s) for device {selected_serial}")

        if latest_archive is None:
            print("No archives found.")
            return

        if not latest_archive.filename:
            raise RuntimeError("Latest archive does not include a filename")

        pprint(asdict(latest_archive))
        archive_data = await thermoworks.get_archive(latest_archive.filename)
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
