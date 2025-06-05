"""Demonstrates how to use this library to get information about the logged in user.

This example shows how to:
1. Authenticate with the Thermoworks Cloud API
2. Get user information
3. Print detailed information about the user and their properties
"""

import asyncio
import json
import os
import pprint
from dataclasses import asdict

from aiohttp import ClientSession

from thermoworks_cloud import AuthFactory, ThermoworksCloud

# Make sure these are defined
email = os.environ["THERMOWORKS_EMAIL"]
password = os.environ["THERMOWORKS_PASSWORD"]


async def __main__():
    # Use a context manager when providing the session to the auth factory
    async with ClientSession() as session:
        auth = await AuthFactory(session).build_auth(email, password)
        thermoworks = ThermoworksCloud(auth)
        user = await thermoworks.get_user()

        # Print user information
        print(f"\n{'=' * 50}")
        print(f"USER: {user.display_name or user.email or 'Unknown'}")
        print(f"UID: {user.uid}")
        print(f"ACCOUNT ID: {user.account_id}")
        print(f"{'=' * 50}")

        # Print user properties
        print("\nUSER PROPERTIES:")
        user_dict = asdict(user)
        pprint.pprint(user_dict, compact=False)

        # Print device count
        device_count = 0
        if user.device_order and user.account_id in user.device_order:
            device_count = len(user.device_order[user.account_id])
        print(f"\nDEVICES: {device_count}")

        # Save the data to a JSON file for further analysis
        with open("thermoworks_user_data.json", "w") as f:
            json.dump(user_dict, f, indent=2, default=str)

        print("\nData saved to thermoworks_user_data.json for further analysis")


asyncio.run(__main__())
