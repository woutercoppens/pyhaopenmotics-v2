"""Module containing a LocalGateway Client for the OpenMotics API."""

from __future__ import annotations

import logging
import ssl
import time
from typing import Any

import aiohttp
from yarl import URL

from pyhaopenmotics.helpers import get_ssl_context
from pyhaopenmotics.openmoticsgw.energy import OpenMoticsEnergySensors
from pyhaopenmotics.openmoticsgw.groupactions import OpenMoticsGroupActions
from pyhaopenmotics.openmoticsgw.lights import OpenMoticsLights
from pyhaopenmotics.openmoticsgw.outputs import OpenMoticsOutputs
from pyhaopenmotics.openmoticsgw.sensors import OpenMoticsSensors
from pyhaopenmotics.openmoticsgw.shutters import OpenMoticsShutters
from pyhaopenmotics.openmoticsgw.thermostats import OpenMoticsThermostats

# from .errors import (
#     AuthenticationException,
#     OpenMoticsConnectionError,
#     OpenMoticsConnectionSslError,
#     OpenMoticsConnectionTimeoutError,
# )
from .omclient import OMClient

_LOGGER = logging.getLogger(__name__)

LOCAL_TOKEN_EXPIRES_IN = 3600
CLOCK_OUT_OF_SYNC_MAX_SEC = 20


class LocalGateway(OMClient):

    """Docstring."""

    _close_session: bool = False

    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        *,
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession | None = None,
        tls: bool = False,
        ssl_context: ssl.SSLContext | None = None,
        port: int = 443,
    ) -> None:
        """Initialize connection with the OpenMotics LocalGateway API.

        Args:
        ----
            host: Hostname or IP address of the AdGuard Home instance.
            password: Password for HTTP auth, if enabled.
            port: Port on which the API runs, usually 3000.
            request_timeout: Max timeout to wait for a response from the API.
            session: Optional, shared, aiohttp client session.
            tls: True, when TLS/SSL should be used.
            username: Username for HTTP auth, if enabled.
            ssl_context: ssl.SSLContext.
        """
        super().__init__(
            host=host,
            token=None,
            request_timeout=request_timeout,
            session=session,
        )
        self.token_expires_at: float = 0

        self.password = password
        self.port = port
        self.request_timeout = request_timeout
        self.tls = tls
        self.username = username

        self.auth = None
        if self.username and self.password:
            _LOGGER.debug("LocalGateway setting self.auth")
            self.auth = {"username": self.username, "password": self.password}

        if ssl_context is not None:
            self.ssl_context = ssl_context
        else:
            self.ssl_context = get_ssl_context(verify_ssl=self.tls)

    async def exec_action(
        self,
        path: str,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
    ) -> Any:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
        ----
            path: path
            data: dict
            headers: dict

        Returns:
        -------
            response json or text
        """
        # Try to execute the action.
        return await self._request(
            path,
            method=aiohttp.hdrs.METH_POST,
            data=data,
            headers=await self._get_auth_headers(headers),
        )

    async def get_token(self) -> None:
        """Login to the gateway: sets the token in the connector."""
        resp = await self._request(
            path="login",
            data=self.auth,
        )
        if resp["success"] is True:
            self.token = resp["token"]
            self.token_expires_at = time.time() + LOCAL_TOKEN_EXPIRES_IN
        else:
            self.token = None
            self.token_expires_at = 0

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
        url = str(
            URL.build(scheme=scheme, host=self.host, port=self.port, path="/").join(URL(path))
        )
        return url

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
        if self.token is None or self.token_expires_at < time.time() + CLOCK_OUT_OF_SYNC_MAX_SEC:
            await self.get_token()

        if headers is None:
            headers = {}

        headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.token}",
            }
        )
        return headers

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
        # implemented to be compatible with cloud
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
    def energysensors(self) -> OpenMoticsEnergySensors:
        """Get energy sensors.

        Returns
        -------
            OpenMoticsEnergySensors
        """
        return OpenMoticsEnergySensors(self)

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

    async def __aenter__(self) -> LocalGateway:
        """Async enter.

        Returns
        -------
            LocalGateway: The LocalGateway object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
        ----
            *_exc_info: Exec type.
        """
        await self.close()
