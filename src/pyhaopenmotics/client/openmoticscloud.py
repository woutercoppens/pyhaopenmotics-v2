"""Module containing a OpenMoticsCloud Client for the OpenMotics API."""

from __future__ import annotations

import logging
from collections.abc import Awaitable, Callable
from typing import Any

import aiohttp
from yarl import URL

from pyhaopenmotics.cloud.groupactions import OpenMoticsGroupActions
from pyhaopenmotics.cloud.installations import OpenMoticsInstallations
from pyhaopenmotics.cloud.lights import OpenMoticsLights
from pyhaopenmotics.cloud.models.installation import Installation
from pyhaopenmotics.cloud.outputs import OpenMoticsOutputs
from pyhaopenmotics.cloud.sensors import OpenMoticsSensors
from pyhaopenmotics.cloud.shutters import OpenMoticsShutters
from pyhaopenmotics.cloud.thermostats import OpenMoticsThermostats
from pyhaopenmotics.helpers import base64_encode

from .const import CLOUD_API_URL
from .omclient import OMClient

# from .errors import OpenMoticsConnectionError, OpenMoticsConnectionTimeoutError


_LOGGER = logging.getLogger(__name__)


class OpenMoticsCloud(OMClient):

    """Docstring."""

    _installations: list[Installation] | None
    _close_session: bool = False

    def __init__(
        self,
        token: str,
        *,
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession | None = None,
        token_refresh_method: Callable[[], Awaitable[str]] | None = None,
        installation_id: int | None = None,
        base_url: str = CLOUD_API_URL,
    ) -> None:
        """Initialize connection with the OpenMotics Cloud API.

        Args:
        ----
            token: str
            request_timeout: int
            session: aiohttp.client.ClientSession
            token_refresh_method: token refresh function
            installation_id: int
            base_url: str

        """
        super().__init__(
            host=CLOUD_API_URL,
            token=token,
            request_timeout=request_timeout,
            session=session,
        )
        self._installation_id = installation_id
        self.base_url = base_url

        self.token_refresh_method = token_refresh_method

        self.ws_subscribe_data.update(
            {
                "installation_ids": [
                    f"{self._installation_id}",
                ],
            }
        )

    @property
    def installation_id(self) -> int | None:
        """Get installation id.

        Returns
        -------
            The installation id that will be used for this session.

        """
        return self._installation_id

    @installation_id.setter
    def installation_id(self, installation_id: int) -> None:
        """Set installation id.

        Args:
        ----
            installation_id: The installation id that will be used
                for this session.

        """
        self._installation_id = installation_id

    async def _get_url(self, path: str, scheme: str | None = None) -> str:
        """Update the auth headers to include a working token.

        Args:
        ----
            path: str
            scheme: str

        Returns:
        -------
            url: str

        """
        url = URL(f"{self.base_url}{path}")
        if scheme is not None:
            url = url.with_scheme(scheme)
        return str(url)

    async def _get_auth_headers(
        self,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update the auth headers to include a working token.

        Args:
        ----
            headers: dict

        Returns:
        -------
            headers

        """
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()

        if headers is None:
            headers = {}

        headers.update(
            {
                # "User-Agent": self.user_agent,
                # "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.token}",
            }
        )
        return headers

    async def _get_ws_headers(
        self,
        headers: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Update the auth headers to include a working token.

        Args:
        ----
            headers: dict

        Returns:
        -------
            headers

        """
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()

        if headers is None:
            headers = {}

        base64_message = base64_encode(self.token)

        # base64_message = 'ejVvaGE1dzdkbDZxdHNhbG1rZWZoczhoMGhlaTh6OGo'
        print(base64_message)

        headers.update(
            {
                # "User-Agent": self.user_agent,
                # "Authorization": f"Bearer {self.token}",
                "Sec-WebSocket-Protocol": f"authorization.bearer.{base64_message}",
                # "Sec-WebSocket-Extensions": "permessage-deflate",
                "Origin": "https://api.openmotics.com",
                "Connection": "Upgrade",
                "Upgrade": "websocket",
                "Sec-Fetch-Dest": "websocket",
                "Sec-Fetch-Mode": "websocket",
                "Sec-Fetch-site": "same-site",
            }
        )
        return headers

    async def _get_ws_protocols(
        self,
    ) -> str:
        """Update the auth headers to include a working token.

        Args:
        ----
            headers: dict

        Returns:
        -------
            headers

        """
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()
        base64_message = base64_encode(self.token)
        protocols = f"authorization.bearer.{base64_message}"

        return protocols

    @property
    def installations(self) -> OpenMoticsInstallations:
        """Get installations.

        Returns
        -------
            OpenMoticsInstallations

        """
        return OpenMoticsInstallations(self)

    @property
    def outputs(self) -> OpenMoticsOutputs:
        """Get outputs.

        Returns
        -------
            OpenMoticsOutputs

        """
        return OpenMoticsOutputs(self)

    @property
    def groupactions(self) -> OpenMoticsGroupActions:
        """Get groupactions.

        Returns
        -------
            OpenMoticsGroupActions

        """
        return OpenMoticsGroupActions(self)

    @property
    def lights(self) -> OpenMoticsLights:
        """Get lights.

        Returns
        -------
            OpenMoticsLights

        """
        return OpenMoticsLights(self)

    @property
    def sensors(self) -> OpenMoticsSensors:
        """Get sensors.

        Returns
        -------
            OpenMoticsSensors

        """
        return OpenMoticsSensors(self)

    @property
    def shutters(self) -> OpenMoticsShutters:
        """Get shutters.

        Returns
        -------
            OpenMoticsShutters

        """
        return OpenMoticsShutters(self)

    @property
    def thermostats(self) -> OpenMoticsThermostats:
        """Get thermostats.

        Returns
        -------
            OpenMoticsThermostats

        """
        return OpenMoticsThermostats(self)

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> OpenMoticsCloud:
        """Async enter.

        Returns
        -------
            OpenMoticsCloud: The OpenMoticsCloud object.

        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
        ----
            *_exc_info: Exec type.

        """
        await self.close()
