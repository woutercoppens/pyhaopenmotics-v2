"""Module containing a OpenMoticsCloud Client for the OpenMotics API."""

from __future__ import annotations

import asyncio
import json
import logging
import socket
import traceback
from typing import TYPE_CHECKING, Any

import aiohttp
import async_timeout
import backoff
import websockets
from yarl import URL

from .__version__ import __version__

if TYPE_CHECKING:
    from collections.abc import Awaitable, Callable

    from .cloud.models.installation import Installation

from .cloud.groupactions import OpenMoticsGroupActions
from .cloud.inputs import OpenMoticsInputs
from .cloud.installations import OpenMoticsInstallations
from .cloud.lights import OpenMoticsLights
from .cloud.outputs import OpenMoticsOutputs
from .cloud.sensors import OpenMoticsSensors
from .cloud.shutters import OpenMoticsShutters
from .cloud.thermostats import OpenMoticsThermostats
from .const import CLOUD_API_HOST, CLOUD_API_URL, CLOUD_PORTAL_HOST
from .errors import OpenMoticsConnectionError, OpenMoticsConnectionTimeoutError
from .helpers import base64_encode

_LOGGER = logging.getLogger(__name__)


class OpenMoticsCloud:

    """Docstring."""

    _installations: list[Installation] | None
    _wsclient: aiohttp.ClientWebSocketResponse | None = None
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
        self.session = session
        self.token = None if token is None else token.strip()
        self._installation_id = installation_id
        self.base_url = base_url

        self.request_timeout = request_timeout
        self.token_refresh_method = token_refresh_method
        self.user_agent = f"PyHAOpenMotics/{__version__}"

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

    @backoff.on_exception(backoff.expo, OpenMoticsConnectionError, max_tries=3, logger=None)
    async def _request(
        self,
        path: str,
        *,
        method: str = aiohttp.hdrs.METH_GET,
        params: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        scheme: str = "https",
        **kwargs: Any,
    ) -> Any:
        """Make post request using the underlying aiohttp clientsession.

        with the default timeout of 15s. in case of retryable exceptions,
        requests are retryed for up to 10 times or 5 minutes.

        Args:
        ----
            path: path
            method: get of post
            params: dict
            **kwargs: extra args

        Returns:
        -------
            response json or text

        Raises:
        ------
            OpenMoticsConnectionError: An error occurred while communication with
                the OpenMotics API.
            OpenMoticsConnectionTimeoutError: A timeout occurred while communicating
                with the OpenMotics API.
        """
        if self.token_refresh_method is not None:
            self.token = await self.token_refresh_method()

        url = await self._get_url(
            path=path,
            scheme=scheme,
        )
        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

        if params:
            for key, value in params.items():
                if isinstance(value, bool):
                    params[key] = str(value).lower()

        _LOGGER.debug(f"url: {url}")
        _LOGGER.debug(f"headers: {headers}")
        try:
            async with async_timeout.timeout(self.request_timeout):
                resp = await self.session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    **kwargs,
                )

            if _LOGGER.isEnabledFor(logging.DEBUG):
                body = await resp.text()
                _LOGGER.debug(
                    "Request with status=%s, body=%s",
                    resp.status,
                    body,
                )

            resp.raise_for_status()

        except asyncio.TimeoutError as exception:
            msg = "Timeout occurred while connecting to OpenMotics API"
            raise OpenMoticsConnectionTimeoutError(msg) from exception
        except (
            aiohttp.ClientError,
            socket.gaierror,
        ) as exception:
            msg = "Error occurred while communicating with OpenMotics API."
            raise OpenMoticsConnectionError(msg) from exception

        if "application/json" in resp.headers.get("Content-Type", ""):
            response_data = await resp.json()
            return response_data

        return await resp.text()

    async def get(self, path: str, **kwargs: Any) -> Any:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
        ----
            path: string
            **kwargs: any

        Returns:
        -------
            response json or text
        """
        return await self._request(
            path,
            method=aiohttp.hdrs.METH_GET,
            **kwargs,
        )

    async def post(self, path: str, **kwargs: Any) -> Any:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
        ----
            path: path
            **kwargs: extra args

        Returns:
        -------
            response json or text
        """
        return await self._request(
            path,
            method=aiohttp.hdrs.METH_POST,
            **kwargs,
        )

    async def _get_url(self, path: str, scheme: str = "https") -> str:
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
        if scheme != "https":
            url = URL(url).with_scheme(scheme)
        return str(url)

    # async def subscribe_webhook(self) -> None:
    #     """Register a webhook with OpenMotics for live updates."""
    #     # Register webhook
    #     await self._request(
    #         "/ws/events",
    #                 "types": [
    #                     "OUTPUT_CHANGE",
    #                     "SENSOR_CHANGE",
    #                     "SHUTTER_CHANGE",
    #                     "THERMOSTAT_CHANGE",
    #                     "THERMOSTAT_GROUP_CHANGE",
    #                     "VENTILATION_CHANGE",
    #                 ],
    #             },
    #         },

    # async def unsubscribe_webhook(self) -> None:
    #     """Delete all webhooks for this application ID."""
    #     await self._request(
    #         "/ws/events",

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
        # if self.token is None or self.token_expires_at < time.time() + CLOCK_OUT_OF_SYNC_MAX_SEC:

        if headers is None:
            headers = {}

        headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "application/json, text/plain, */*",
                "Authorization": f"Bearer {self.token}",
            },
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
        # if self.token is None or self.token_expires_at < time.time() + CLOCK_OUT_OF_SYNC_MAX_SEC:

        if headers is None:
            headers = {}

        base64_message = base64_encode(self.token)

        headers.update(
            {
                # "User-Agent": self.user_agent,
                "Sec-WebSocket-Protocol": f"authorization.bearer.{base64_message}",
                # "Sec-WebSocket-Extensions": "permessage-deflate",
                "host": CLOUD_API_HOST,
                "Origin": CLOUD_PORTAL_HOST,
                "Connection": "Upgrade",
                "Upgrade": "websocket",
                "accept-encoding": "gzip, deflate, br",
                "cache-control": "no-cache",
                "pragma": "no-cache",
                # "Sec-Fetch-Dest": "websocket",
                # "Sec-Fetch-Mode": "websocket",
                # "Sec-Fetch-site": "same-site",
                "user-agent": "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
            },
        )
        return headers

    @property
    def connected(self) -> bool:
        """Return if we are connect to the WebSocket of OpenMotics.

        Returns
        -------
            True if we are connected to the WebSocket,
            False otherwise.
        """
        return self._wsclient is not None and not self._wsclient.closed

    async def connect(self) -> None:
        """Connect to the WebSocket of OpenMotics.

        Raises
        ------
            OpenMoticsError: The configured localgw does not support WebSocket
                communications.
            OpenMoticsConnectionError: Error occurred while communicating with
                OpenMotics via the WebSocket.
        """
        if self.connected:
            return

        # if not self._device:

        if not self.session:
            raise OpenMoticsConnectionError(
                "The OM device at {self.localgw} does not support WebSockets",
            )

        url = await self._get_url(
            path="/ws/events",
            scheme="wss",
        )
        headers = await self._get_ws_headers()

        try:
            self._wsclient = await self.session.ws_connect(
                url=url,
                headers=headers,
            )
        except (
            aiohttp.WSServerHandshakeError,
            aiohttp.ClientConnectionError,
            socket.gaierror,
        ) as exception:
            raise OpenMoticsConnectionError(
                ("Error occurred while communicating with OpenMotics" f" on WebSocket at {url}",),
            ) from exception

    async def connect2(self) -> None:
        """Connect to the WebSocket of OpenMotics.

        Raises
        ------
            OpenMoticsError: The configured localgw does not support WebSocket
                communications.
            OpenMoticsConnectionError: Error occurred while communicating with
                OpenMotics via the WebSocket.
        """
        if self.connected:
            return

        # if not self._device:

        if not self.session:
            raise OpenMoticsConnectionError(
                "The OM device at {self.localgw} does not support WebSockets",
            )

        uri = await self._get_url(
            path="/ws/events",
            scheme="wss",
        )
        extra_headers = await self._get_ws_headers()

        _LOGGER.debug(f"uri: {uri}")
        _LOGGER.debug(f"extra_headers: {extra_headers}")
        try:
            async with websockets.connect(
                uri=uri,
                extra_headers=extra_headers,
            ) as websocket:
                _LOGGER.debug("WebSocket Opened.")
                _LOGGER.debug(json.loads(await websocket.recv()))
                _LOGGER.debug("websocket client connected. looping...")

                while self.loop:
                    data = json.loads(await websocket.recv())
                    if "event" not in data:
                        continue

                    try:
                        self.ws_handler(self, data)
                    except:
                        _LOGGER.error("".join(traceback.format_exc()))

        except websockets.WebSocketException:
            pass

    @property
    def installations(self) -> OpenMoticsInstallations:
        """Get installations.

        Returns
        -------
            OpenMoticsInstallations
        """
        return OpenMoticsInstallations(self)

    @property
    def inputs(self) -> OpenMoticsInputs:
        """Get inputs.

        Returns
        -------
            OpenMoticsInputs
        """
        return OpenMoticsInputs(self)

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
