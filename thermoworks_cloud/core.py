"""Accessor for the Thermoworks Cloud API."""

import logging
import urllib.parse
from typing import List, Literal, Optional

from thermoworks_cloud.utils import format_client_response

from .auth import Auth
from .models.archive import (
    ArchiveData,
    ArchivePage,
    _archive_json_to_data,
    _document_to_archive_metadata,
)
from .models.device import Device, _document_to_device
from .models.device_channel import DeviceChannel, _document_to_device_channel
from .models.user import User, document_to_user

_LOGGER = logging.getLogger(__name__)


class ResourceNotFoundError(Exception):
    """Custom exception indicating that the requested resource could not be found."""

    def __init__(
        self,
        message: str,
    ) -> None:
        """Initialize the error."""

        super().__init__(message)
        self.message = message


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

        response = await self._auth.request("get", f"documents/users/{self._auth.user_id}")
        if response.ok:
            user_document = await response.json()
            return document_to_user(user_document)

        if response.status == 404:
            raise ResourceNotFoundError("User not found")

        try:
            error_response = await format_client_response(response)
        except RuntimeError:
            error_response = "Could not read response body."

        raise RuntimeError(f"Failed to get user: {error_response}")

    async def get_device(self, device_serial: str) -> Device:
        """Fetch a device by serial number."""

        response = await self._auth.request("get", f"documents/devices/{device_serial}")
        if response.ok:
            device_document = await response.json()
            return _document_to_device(device_document)

        if response.status == 404:
            raise ResourceNotFoundError(f"Device with serial '{device_serial}' not found")

        try:
            error_response = await format_client_response(response)
        except RuntimeError:
            error_response = "Could not read response body."

        raise RuntimeError(f"Failed to get device: {error_response}")

    async def get_device_channel(
        self, device_serial: str, channel: str
    ) -> DeviceChannel:
        """Fetch channel information for a device."""

        response = await self._auth.request(
            "get", f"documents/devices/{device_serial}/channels/{channel}"
        )
        if response.ok:
            device_channel_document = await response.json()
            return _document_to_device_channel(device_channel_document)

        if response.status == 404:
            raise ResourceNotFoundError(
                f"Device channel with serial '{device_serial}' and channel '{channel}' not found"
            )

        try:
            error_response = await format_client_response(response)
        except RuntimeError:
            error_response = "Could not read response body."

        raise RuntimeError(
            f"Failed to get device channel: {error_response}")

    async def list_device_archives(
        self,
        device_serial: str,
        page_token: Optional[str] = None,
        order: Literal["asc", "desc"] = "desc",
    ) -> ArchivePage:
        """Fetch a page of historical archive metadata for a device.

        Archives are ordered by creation time, newest first by default. Pass
        ``order="asc"`` for oldest first, and pass the returned
        ``next_page_token`` to retrieve the following page.
        """

        if order not in ("asc", "desc"):
            raise ValueError("order must be 'asc' or 'desc'")

        params = {"orderBy": f"createdOn {order}"}
        if page_token:
            params["pageToken"] = page_token

        response = await self._auth.request(
            "get", f"documents/devices/{device_serial}/archive", params=params
        )
        if response.ok:
            archive_response = await response.json()
            return ArchivePage(
                archives=[
                    _document_to_archive_metadata(document)
                    for document in archive_response.get("documents", [])
                ],
                next_page_token=archive_response.get("nextPageToken"),
            )

        if response.status == 404:
            raise ResourceNotFoundError(
                f"Archives for device with serial '{device_serial}' not found"
            )

        try:
            error_response = await format_client_response(response)
        except RuntimeError:
            error_response = "Could not read response body."

        raise RuntimeError(f"Failed to list device archives: {error_response}")

    async def get_archive(self, filename: str) -> ArchiveData:
        """Fetch and parse the readings for a historical archive by filename."""

        quoted_filename = urllib.parse.quote(filename, safe="")
        url = (
            f"{self._auth.storage_url_root}/v0/b/{self._auth.storage_bucket}"
            f"/o/{quoted_filename}"
        )
        response = await self._auth.request_url("get", url, params={"alt": "media"})

        if response.ok:
            # ThermoWorks archive objects use text/json rather than application/json.
            # We set content_type=None to bypass the content type check in aiohttp.
            archive_json = await response.json(content_type=None)
            return _archive_json_to_data(archive_json, filename=filename)

        if response.status == 404:
            raise ResourceNotFoundError(f"Archive '{filename}' not found")

        try:
            error_response = await format_client_response(response)
        except RuntimeError:
            error_response = "Could not read response body."

        raise RuntimeError(f"Failed to get archive: {error_response}")

    async def get_devices(self, account_id: str) -> List[Device]:
        """Fetch devices for the authenticated user using Firestore query.

        It queries the Firestore 'devices' collection directly using the user's accountId.
        """

        # Build the Firestore query
        query_body = {
            "structuredQuery": {
                "from": [{"collectionId": "devices"}],
                "where": {
                    "fieldFilter": {
                        "field": {"fieldPath": "accountId"},
                        "op": "EQUAL",
                        "value": {"stringValue": account_id}
                    }
                },
                "orderBy": [{"field": {"fieldPath": "__name__"}, "direction": "ASCENDING"}]
            }
        }

        # Execute the query against Firestore REST API
        headers = {"Content-Type": "application/json"}
        response = await self._auth.request("post", "documents:runQuery",
                                            additional_headers=headers, json=query_body)

        if not response.ok:
            try:
                error_response = await format_client_response(response)
            except RuntimeError:
                error_response = "Could not read response body."
            raise RuntimeError(f"Failed to query devices: {error_response}")

        # Process the response
        result = await response.json()
        devices = []

        for item in result:
            if "document" in item:
                device = _document_to_device(item["document"])
                devices.append(device)

        return devices
