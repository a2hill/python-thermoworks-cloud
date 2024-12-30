"""Demonstrates how to use this library to get information about the logged in user."""

import asyncio
import os
from aiohttp import ClientSession

from thermoworks_cloud import AuthFactory, ThermoworksCloud

email = os.environ["THERMOWORKS_EMAIL"]
password = os.environ["THERMOWORKS_PASSWORD"]


async def __main__():
    # User a context manager when providing the session to the auth factory
    async with ClientSession() as session:
        auth = await AuthFactory(session).build_auth(email, password)
        thermoworks = ThermoworksCloud(auth)
        user = await thermoworks.get_user()
        assert user is not None


asyncio.run(__main__())
