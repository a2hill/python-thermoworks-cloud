"""Accessor for the Thermoworks Cloud API."""

import logging

from thermoworks_cloud.utils import format_client_response

from .auth import Auth
from .models.device import Device, _document_to_device
from .models.device_channel import DeviceChannel, _document_to_device_channel
from .models.user import User, document_to_user

_LOGGER = logging.getLogger(__name__)


class ThermoworksCloud:
    """Client for the Thermoworks Cloud service."""

    def __init__(self, auth: Auth) -> None:
        """Create a new client. `thermoworks_cloud.Auth` objects are created using a 
        `thermoworks_cloud.AuthFactory`.

        Args:
            auth (Auth): Authorization object used to make authorized requests to the service.
        """
        self._auth = auth

    async def get_user(self) -> User:
        """Fetch information for the authenticated user."""

        try:
            response = await self._auth.request("get", f"users/{self._auth.user_id}")
            if response.ok:
                user_document = await response.json()
                return document_to_user(user_document)

            try:
                error_response = await format_client_response(response)
            except RuntimeError:
                error_response = "Could not read response body."
            _LOGGER.error(
                "Received error response while getting user: %s", error_response
            )

            response.raise_for_status()

        except Exception as e:
            raise RuntimeError("Failed to get user") from e

    async def get_device(self, device_serial: str) -> Device:
        """Fetch a device by serial number."""

        try:
            response = await self._auth.request("get", f"devices/{device_serial}")
            if response.ok:
                device_document = await response.json()
                return _document_to_device(device_document)

            try:
                error_response = await format_client_response(response)
            except RuntimeError:
                error_response = "Could not read response body."
            _LOGGER.error(
                "Received error response while getting device: %s", error_response
            )

            response.raise_for_status()

        except Exception as e:
            raise RuntimeError("Failed to get device") from e

    async def get_device_channel(
        self, device_serial: str, channel: str
    ) -> DeviceChannel:
        """Fetch channel information for a device."""

        try:
            response = await self._auth.request(
                "get", f"devices/{device_serial}/channels/{channel}"
            )
            if response.ok:
                device_channel_document = await response.json()
                return _document_to_device_channel(device_channel_document)

            try:
                error_response = await format_client_response(response)
            except RuntimeError:
                error_response = "Could not read response body."
            _LOGGER.error(
                "Received error response while getting device channel: %s",
                error_response,
            )

            response.raise_for_status()

        except Exception as e:
            raise RuntimeError("Failed to get device channel") from e
