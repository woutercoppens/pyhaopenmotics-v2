"""Module containing a ThermostatClient for the Netatmo API."""

from __future__ import annotations

import logging
import asyncio
import ssl
from importlib.abc import InspectLoader
import socket
from dataclasses import dataclass
from importlib import metadata
from typing import Any, Optional, TypedDict
import aiohttp

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    stop_after_delay,
    wait_random_exponential,
)
from yarl import URL

import async_timeout

from aiohttp.client import ClientError, ClientResponseError

from .__version__ import __version__
from .errors import ApiException, RequestUnauthorizedException, NetworkTimeoutException, RequestBackoffException, RetryableException, client_error_handler

from .openmoticsgw.outputs import OpenMoticsOutputs

class LocalGateway:
    """Docstring."""

    _status: Optional[Status] = None
    _close_session: bool = False

    _webhook_refresh_timer_task: Optional[asyncio.TimerHandle] = None
    _webhook_url: Optional[str] = None    

    def __init__(
        self,
        username: str,
        password: str,
        localgw: str,
        *,
        request_timeout: int = 8,
        session: Optional[aiohttp.client.ClientSession] = None,
        tls: bool = False,
        # verify_ssl: bool = False,
        ssl_context: ssl.SSLContext = None,
        port: int = 443,
        user_agent: str | None = None,
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
            verify_ssl: Can be set to false, when TLS with self-signed cert is used.
        """
        self._session: aiohttp.client.ClientSession = session
        self._close_session = False

        self.token = None

        self.localgw = localgw
        self.password = password
        self.port = port
        self.request_timeout = request_timeout
        self.tls = tls
        self.username = username
        # self.verify_ssl = verify_ssl   
        self.ssl_context = ssl_context

        self.user_agent = user_agent

        if user_agent is None:
            version = metadata.version(__package__)
            self.user_agent = f"pyhaopenmotics/{version}"

        self.auth = None
        if self.username and self.password:
            print('setting self.auth')
            self.auth = { "username" : self.username, "password" : self.password }

        self.outputs = OpenMoticsOutputs(self)

    # @retry(
    #     retry=retry_if_exception_type(RetryableException),
    #     stop=(stop_after_delay(300) | stop_after_attempt(10)),
    #     wait=wait_random_exponential(multiplier=1, max=30),
    #     reraise=True,
    # )
    async def _request(
        self,
        path: str, 
        *,
        method: str = aiohttp.hdrs.METH_POST, 
        data: dict = None,
        **kwargs,
    ) -> Any:
        """Make post request using the underlying httpx AsyncClient.

        with the default timeout of 15s. in case of retryable exceptions,
        requests are retryed for up to 10 times or 5 minutes.

        Args:
            path: path
            **kwargs: extra args

        Returns:
            response json or text
        """
        scheme = "https" if self.tls else "http"
        url = URL.build(
            scheme=scheme, host=self.localgw, port=self.port, path="/"
        ).join(URL(path))

        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json, text/plain, */*",
        }

        data = self.get_post_data(data)

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        try:
            async with async_timeout.timeout(self.request_timeout):
                resp = await self._session.request(
                    method,
                    url,
                    # auth=self.auth,
                    data=data,
                    # verify_ssl=self.verify_ssl,
                    ssl=self.ssl_context,
                    **kwargs,
                )

            resp.raise_for_status()

        except asyncio.TimeoutError as exception:
            raise ApiException(
                "Timeout occurred while connecting to OpenMotics API"
            ) from exception
        except (
            ClientError,
            ClientResponseError,
            socket.gaierror,
        ) as exception:
            raise ApiException(
                "Error occurred while communicating with OpenMotics API."
            ) from exception

        if "application/json" in resp.headers.get("Content-Type", ""):
            response_data = await resp.json()
            return response_data

        return await resp.text()  # type: ignore

    async def exec_action(
        self, 
        path: str, 
        data: dict = {},
        **kwargs
    ) -> dict[str, Any]:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
            path: path
            **kwargs: extra args

        Returns:
            response json or text
        """
        if self.token == None:
            self.login()

        return await self._request(
            path,
            method=aiohttp.hdrs.METH_POST,
            data=data,
            **kwargs,
        )

    def get_post_data(self, data):
        """ Get the full post data dict, this method adds the token to the dict. """
        if data is not None:
            d = data.copy()
        else:
            d = {}
        if self.token != None:
            d["token"] = self.token
        return d

    async def login(self):
        """ Login to the gateway: sets the token in the connector. """
        print('in login')
        resp = await self._request(
            path="login", 
            data=self.auth,
        ) 

        self.token = resp["token"]
        print(self.token)

    # async def subscribe_webhook(self, installation_id: str, url: str) -> None:
    #     """Register a webhook with OpenMotics for live updates."""

    #     # Register webhook
    #     await self._request(
    #         "/ws/events",
    #         method=aiohttp.hdrs.METH_POST,
    #         data={
    #             "action": "set_subscription",
    #             "types": ["OUTPUT_CHANGE", "SHUTTER_CHANGE", "THERMOSTAT_CHANGE", "THERMOSTAT_GROUP_CHANGE" ],
    #             "installation_ids": [installation_id],
    #         },
    #     )

    # async def unsubscribe_webhook(self, installation_id: str) -> None:
    #     """Delete all webhooks for this application ID."""
    #     await self._request(
    #         "/ws/events",
    #         method=aiohttp.hdrs.METH_DELETE,
    #     )
      
    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> OpenMoticsCloud:
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()