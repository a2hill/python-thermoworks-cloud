"""Demonstrates how to use this library to get information about the account of an API key.

This example shows how to:
1. Create a client using an API key
2. Get account information
3. Print detailed information about the account and its limits
"""

import asyncio
import json
import os
import pprint
from dataclasses import asdict

from aiohttp import ClientSession

from thermoworks_cloud import ThermoworksClient

# Make sure this is defined
api_key = os.environ["THERMOWORKS_KEY"]

# This differs between cloud providers
BASE_URL = "https://cloud.thermoworks.com/api"


async def __main__():
    # Use a context manager when providing the session to the client
    async with ClientSession() as session:
        thermoworks = ThermoworksClient(session, api_key, BASE_URL)
        account = await thermoworks.get_me()

        # Print account information
        print(f"\n{'=' * 50}")
        print(f"ACCOUNT ID: {account.account_id}")
        print(f"RECOMMENDED POLL SECONDS: {account.recommended_poll_seconds}")
        print(f"{'=' * 50}")

        # Print account properties
        print("\nACCOUNT PROPERTIES:")
        account_dict = asdict(account)
        pprint.pprint(account_dict, compact=False)

        # Save the data to a JSON file for further analysis
        with open("thermoworks_account_data.json", "w", encoding="utf-8") as f:
            json.dump(account_dict, f, indent=2, default=str)

        print("\nData saved to thermoworks_account_data.json for further analysis")


asyncio.run(__main__())
