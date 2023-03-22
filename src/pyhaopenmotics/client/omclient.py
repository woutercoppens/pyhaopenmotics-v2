"""Module containing a generic Client for the OpenMotics API."""

from __future__ import annotations

import asyncio
import logging
import socket
from abc import ABC, abstractmethod
from collections.abc import Callable
from typing import Any

import aiohttp
import async_timeout
import backoff
import websockets

from pyhaopenmotics.__version__ import __version__

from .const import WS_SUBSCRIPTION
from .errors import (
    AuthenticationException,
    OpenMoticsConnectionClosed,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
    OpenMoticsError,
)

_LOGGER = logging.getLogger(__name__)


class OMClient(ABC):

    """Docstring."""

    _wsclient: aiohttp.ClientWebSocketResponse | None = None
    _close_session: bool = False

    def __init__(
        self,
        host: str,
        *,
        request_timeout: int = 8,
        session: aiohttp.client.ClientSession | None = None,
        token: str | None = None,
    ) -> None:
        """Initialize general connection with the OpenMotics API.

        Args:
        ----
            token: str
            request_timeout: int
            session: aiohttp.client.ClientSession
            host: str
            token_refresh_method: token refresh function
            installation_id: int
            base_url: str
            username: str
            password: str
            tls: boolean
            ssl_context: ssl.SSLContext
            port: int
        """
        self.session = session
        self.request_timeout = request_timeout
        self.host = host
        self.token = None if token is None else token.strip()

        self.ws_subscribe_data = WS_SUBSCRIPTION

        self.user_agent = f"PyHAOpenMotics/{__version__}"

    @backoff.on_exception(backoff.expo, OpenMoticsConnectionError, max_tries=3, logger=None)
    async def _request(
        self,
        path: str,
        *,
        method: str = aiohttp.hdrs.METH_GET,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
        headers: dict[str, Any] | None = None,
        scheme: str | None = None,
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
            data: dict
            headers: dict
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
        url = await self._get_url(path, scheme)
        headers = await self._get_auth_headers(headers)

        if self.session is None:
            # self.session = aiohttp.ClientSession(trust_env=True)
            self.session = aiohttp.ClientSession()
            self._close_session = True

        if params:
            for key, value in params.items():
                if isinstance(value, bool):
                    params[key] = str(value).lower()

        try:
            async with async_timeout.timeout(self.request_timeout):
                resp = await self.session.request(
                    method,
                    url,
                    headers=headers,
                    params=params,
                    data=data,
                    proxy="http://192.168.0.126:9090",
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
            raise OpenMoticsConnectionTimeoutError(
                "Timeout occurred while connecting to OpenMotics API"
            ) from exception
        except aiohttp.ClientConnectorSSLError as exception:  # pyright: ignore
            # Expired certificate / Date ISSUE
            # pylint: disable=bad-exception-context
            raise OpenMoticsConnectionSslError("Error with SSL certificate.") from exception
        except aiohttp.ClientResponseError as exception:
            if exception.status in [401, 403]:
                raise AuthenticationException() from exception
            raise OpenMoticsConnectionError(
                "Error occurred while communicating with OpenMotics API."
            ) from exception
        except (socket.gaierror, aiohttp.ClientError) as exception:
            raise OpenMoticsConnectionError(
                "Error occurred while communicating with OpenMotics API."
            ) from exception

        if "application/json" in resp.headers.get("Content-Type", ""):
            response_data = await resp.json()
            return response_data

        return await resp.text()

    @abstractmethod
    async def _get_url(self, path: str, scheme: str | None = None) -> str:
        """Update the auth headers to include a working token.

        Args:
        ----
            path: str
            scheme: str

        Returns:
        -------
            url: str
        Subclass must override.
        """
        raise NotImplementedError("Subclass must override.")

    @abstractmethod
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

        Subclass must override.
        """
        raise NotImplementedError("Subclass must override.")

    @abstractmethod
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

        Subclass must override.
        """
        raise NotImplementedError("Subclass must override.")

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
        response = await self._request(
            path,
            method=aiohttp.hdrs.METH_GET,
            **kwargs,
        )
        return response

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
        response = await self._request(
            path,
            method=aiohttp.hdrs.METH_POST,
            **kwargs,
        )
        return response

    # async def subscribe_webhook(self) -> None:
    #     """Register a webhook with OpenMotics for live updates."""
    #     # Register webhook
    #     await self._request(
    #         "/ws/events",
    #         method=aiohttp.hdrs.METH_POST,
    #         scheme="wss",
    #         data=self.ws_subscribe_data,
    #     )

    # async def unsubscribe_webhook(self) -> None:
    #     """Delete all webhooks for this application ID."""
    #     await self._request(
    #         "/ws/events",
    #         method=aiohttp.hdrs.METH_DELETE,
    #         scheme="wss",
    #     )

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
            OpenMoticsError: The configured WLED device, does not support WebSocket
                communications.
            OpenMoticsConnectionError: Error occurred while communicating with
                OpenMotics via the WebSocket.
        """
        if self.connected:
            return

        # if not self._device:
        # await self.update()

        if not self.session:
            raise OpenMoticsError("The WLED device at {self.host} does not support WebSockets")

        url = await self._get_url(
            path="/ws/events",
            scheme="wss",
        )
        headers = await self._get_ws_headers()
        await self._get_ws_protocols()

        try:
            self._wsclient = await self.session.ws_connect(
                url="wss://api.openmotics.com/api/v1.1/ws/events",
                # protocols=protocols,
                headers=headers,
                heartbeat=30,
                proxy="http://192.168.0.126:9090",
            )
        except (
            aiohttp.WSServerHandshakeError,
            aiohttp.ClientConnectionError,
            socket.gaierror,
        ) as exception:
            raise OpenMoticsConnectionError(
                "Error occurred while communicating with OpenMotics" f" on WebSocket at {url}"
            ) from exception

    async def connect2(self) -> None:
        """Connect to the WebSocket of OpenMotics.

        Raises
        ------
            OpenMoticsError: The configured WLED device, does not support WebSocket
                communications.
            OpenMoticsConnectionError: Error occurred while communicating with
                OpenMotics via the WebSocket.
        """
        if self.connected:
            return

        # if not self._device:
        # await self.update()

        if not self.session:
            raise OpenMoticsError("This installation at {self.host} does not support WebSockets")

        await self._get_url(
            # path="/ws/events",
            path="/ws",
            scheme="wss",
        )
        headers = await self._get_ws_headers()

        try:
            get_ssl_context(
                "wss://api.openmotics.com/api/v1.1/ws/events",
                verify,
            )
            async with websockets.client.connect(
                "wss://api.openmotics.com/api/v1.1/ws/events",
                # compression=None,
                extra_headers=headers,
                # subprotocols=[self._get_ws_protocols()],
                close_timeout=0,
            ) as websocket:
                _LOGGER.info("WebSocket Opened.")

                await websocket.send("Hello world!")
                await websocket.recv()
                await websocket.send(self.ws_subscribe_data)

        except websockets.WebSocketException:
            pass

        # except (
        #     aiohttp.WSServerHandshakeError,
        #     aiohttp.ClientConnectionError,
        #     socket.gaierror,
        # ) as exception:
        #     raise OpenMoticsConnectionError(
        #         "Error occurred while communicating with OpenMotics"
        #         f" on WebSocket at {url}"
        #     ) from exception

    async def listen(
        self,
        callback: Callable[[Any], Any],
    ) -> None:
        """Listen for events on the OpenMotics WebSocket.

        Args:
        ----
            callback: Method to call when a state update is received.

        Raises:
        ------
            OpenMoticsError: Not connected to a WebSocket.
            OpenMoticsConnectionError: An connection error occurred while connected
                to the WebSocket
            OpenMoticsConnectionClosed: The WebSocket connection to the remote
                has been closed.
        """
        if not self._wsclient or not self.connected:
            raise OpenMoticsError("Not connected to the OpenMotics WebSocket")

        while not self._wsclient.closed:
            message = await self._wsclient.receive()

            if message.type == aiohttp.WSMsgType.ERROR:
                raise OpenMoticsConnectionError(self._wsclient.exception())

            if message.type == aiohttp.WSMsgType.TEXT:
                message_data = message.json()
                callback(message_data)

            if message.type in (
                aiohttp.WSMsgType.CLOSE,
                aiohttp.WSMsgType.CLOSED,
                aiohttp.WSMsgType.CLOSING,
            ):
                raise OpenMoticsConnectionClosed(
                    f"Connection to the OpenMotics WebSocket on {self.host} has been closed"
                )

    async def disconnect(self) -> None:
        """Disconnect from the WebSocket of OpenMotics."""
        if not self._wsclient or not self.connected:
            return

        await self._wsclient.close()

    async def close(self) -> None:
        """Close open client (WebSocket) session."""
        await self.disconnect()
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> OMClient:
        """Async enter.

        Returns
        -------
            OMClient: The OMClient object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
        ----
            *_exc_info: Exec type.
        """
        await self.close()
