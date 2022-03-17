"""Module containing a LocalGateway Client for the OpenMotics API."""

from __future__ import annotations

import asyncio
import socket
import ssl
from typing import Any, Optional

import aiohttp
import async_timeout
import backoff
from aiohttp.client import ClientError, ClientResponseError
from yarl import URL

from .__version__ import __version__
from .errors import (
    AuthenticationException,
    OpenMoticsConnectionError,
    OpenMoticsConnectionTimeoutError,
)
from .openmoticsgw.groupactions import OpenMoticsGroupActions
from .openmoticsgw.lights import OpenMoticsLights
from .openmoticsgw.outputs import OpenMoticsOutputs
from .openmoticsgw.sensors import OpenMoticsSensors
from .openmoticsgw.shutters import OpenMoticsShutters
from .openmoticsgw.thermostats import OpenMoticsThermostats


class LocalGateway:
    """Docstring."""

    _close_session: bool = False

    def __init__(
        self,
        username: str,
        password: str,
        localgw: str,
        *,
        request_timeout: int = 8,
        session: Optional[aiohttp.client.ClientSession] | None = None,
        tls: bool = False,
        # verify_ssl: bool = False,
        ssl_context: ssl.SSLContext | None = None,
        port: int = 443,
    ) -> None:
        """Initialize connection with the OpenMotics LocalGateway API.

        Args:
            localgw: Hostname or IP address of the AdGuard Home instance.
            password: Password for HTTP auth, if enabled.
            port: Port on which the API runs, usually 3000.
            request_timeout: Max timeout to wait for a response from the API.
            session: Optional, shared, aiohttp client session.
            tls: True, when TLS/SSL should be used.
            username: Username for HTTP auth, if enabled.
            ssl_context: ssl.SSLContext.
        """
        self.session = session
        self.token = None

        self.localgw = localgw
        self.password = password
        self.port = port
        self.request_timeout = request_timeout
        self.tls = tls
        self.username = username
        # self.verify_ssl = verify_ssl
        self.ssl_context = ssl_context

        self.user_agent = f"PyHAOpenMotics/{__version__}"

        self.auth = None
        if self.username and self.password:
            print("setting self.auth")
            self.auth = {"username": self.username, "password": self.password}

        self.outputs = OpenMoticsOutputs(self)
        self.sensors = OpenMoticsSensors(self)
        self.groupactions = OpenMoticsGroupActions(self)
        self.shutters = OpenMoticsShutters(self)
        self.thermostats = OpenMoticsThermostats(self)
        # implemented to be compatible with cloud
        self.lights = OpenMoticsLights(self)

    @backoff.on_exception(
        backoff.expo, OpenMoticsConnectionError, max_tries=3, logger=None
    )
    async def _request(
        self,
        path: str,
        *,
        method: str = aiohttp.hdrs.METH_POST,
        data: dict[str, Any] | None = None,
        **kwargs: Any,
    ) -> Any:
        """Make post request using the underlying httpx AsyncClient.

        with the default timeout of 15s. in case of retryable exceptions,
        requests are retryed for up to 10 times or 5 minutes.

        Args:
            path: path
            method: post
            data: dict
            **kwargs: extra args

        Returns:
            response json or text

        Raises:
            OpenMoticsConnectionError: An error occurred while communitcation with
                the OpenMotics API.
            OpenMoticsConnectionTimeoutError: A timeout occurred while communicating
                with the OpenMotics API.
            AuthenticationException: raised when token is expired.
        """
        url = URL.build(
            scheme="https", host=self.localgw, port=self.port, path="/"
        ).join(URL(path))

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
        }

        data = self.get_post_data(data)

        if self.session is None:
            self.session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                resp = await self.session.request(
                    method,
                    url,
                    data=data,
                    # verify_ssl=self.verify_ssl,
                    ssl=self.ssl_context,
                    headers=headers,
                    **kwargs,
                )

            resp.raise_for_status()

        except asyncio.TimeoutError as exception:
            raise OpenMoticsConnectionTimeoutError(
                "Timeout occurred while connecting to OpenMotics API"
            ) from exception
        except ClientResponseError as exception:
            if exception.status in [401, 403]:
                raise AuthenticationException() from exception
            raise OpenMoticsConnectionError(
                "Error occurred while communicating with OpenMotics API."
            ) from exception
        except (socket.gaierror, ClientError) as exception:
            raise OpenMoticsConnectionError(
                "Error occurred while communicating with OpenMotics API."
            ) from exception

        if "application/json" in resp.headers.get("Content-Type", ""):
            response_data = await resp.json()
            return response_data

        return await resp.text()

    async def exec_action(
        self, path: str, data: dict[str, Any] | None = None, **kwargs: Any
    ) -> Any:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
            path: path
            data: dict
            **kwargs: extra args

        Returns:
            response json or text
        """
        if self.token is None:
            await self.login()

        try:
            # Try to execute the action.
            return await self._request(
                path,
                method=aiohttp.hdrs.METH_POST,
                data=data,
                **kwargs,
            )
        except AuthenticationException:
            # Get a new token and retry the action.
            await self.login()
            return await self._request(
                path,
                method=aiohttp.hdrs.METH_POST,
                data=data,
                **kwargs,
            )

    def get_post_data(self, data: dict[str, Any] | None = None) -> dict[str, Any]:
        """Get the full post data dict, this method adds the token to the dict.

        Args:
            data: dict

        Returns:
            data with token added
        """
        if data is not None:
            dcopy = data.copy()
        else:
            dcopy = {}
        if self.token is not None:
            dcopy["token"] = self.token
        return dcopy

    async def login(self) -> None:
        """Login to the gateway: sets the token in the connector."""
        resp = await self._request(
            path="login",
            data=self.auth,
        )

        self.token = resp["token"]
        print(self.token)

    async def subscribe_webhook(self, installation_id: str) -> None:
        """Register a webhook with OpenMotics for live updates.

        Args:
            installation_id: int

        """
        # Register webhook
        await self._request(
            "/ws/events",
            method=aiohttp.hdrs.METH_POST,
            data={
                "action": "set_subscription",
                "types": [
                    "OUTPUT_CHANGE",
                    "SHUTTER_CHANGE",
                    "THERMOSTAT_CHANGE",
                    "THERMOSTAT_GROUP_CHANGE",
                ],
                "installation_ids": [installation_id],
            },
        )

    async def unsubscribe_webhook(self) -> None:
        """Delete all webhooks for this application ID."""
        await self._request(
            "/ws/events",
            method=aiohttp.hdrs.METH_DELETE,
        )

    async def close(self) -> None:
        """Close open client session."""
        if self.session and self._close_session:
            await self.session.close()

    async def __aenter__(self) -> LocalGateway:
        """Async enter.

        Returns:
            LocalGateway: The LocalGateway object.
        """
        return self

    async def __aexit__(self, *_exc_info: Any) -> None:
        """Async exit.

        Args:
            *_exc_info: Exec type.
        """
        await self.close()
