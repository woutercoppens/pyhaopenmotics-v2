"""Module containing a ThermostatClient for the Netatmo API."""

from __future__ import annotations

import logging
import asyncio
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
from .const import (
    CLOUD_API_VERSION,
    CLOUD_API_TOKEN_URL,
    CLOUD_API_AUTHORIZATION_URL,
)
from .errors import ApiException, RequestUnauthorizedException, NetworkTimeoutException, RequestBackoffException, RetryableException, client_error_handler

from .cloud.installations import OpenMoticsInstallations
from .cloud.groupactions import OpenMoticsGroupActions
from .cloud.outputs import OpenMoticsOutputs
from .cloud.lights import OpenMoticsLights
from .cloud.sensors import OpenMoticsSensors
from .cloud.shutters import OpenMoticsShutters
from .cloud.thermostats import OpenMoticsThermostats


class OpenMoticsCloud:
    """Docstring."""
    BASE_URL = "https://cloud.openmotics.com/api"

    _installations: Optional[List[Installation]] = None
    _status: Optional[Status] = None
    _close_session: bool = False

    _webhook_refresh_timer_task: Optional[asyncio.TimerHandle] = None
    _webhook_url: Optional[str] = None    

    def __init__(
        self,
        token: str,
        *,
        request_timeout: int = 8,
        session: Optional[aiohttp.client.ClientSession] = None,
        token_refresh_method: Optional[Callable[[], Awaitable[str]]] = None,
        installation_id: Optional[int] = None,
        base_url: str = BASE_URL,
    ) -> None:
        """Initialize connection with the OpenMotics Cloud API.

        Args:
            client_id: str
            client_secret: str
            **kwargs: other arguments
        """
        self._session: aiohttp.client.ClientSession = session
        self.token = None if token is None else token.strip()
        self._installation_id = installation_id
        self.base_url = base_url

        self.request_timeout = request_timeout
        self.token_refresh_method = token_refresh_method
        self.user_agent = f"PyHAOpenMotics/{__version__}"

        self.installations = OpenMoticsInstallations(self)
        self.outputs = OpenMoticsOutputs(self)
        self.groupactions= OpenMoticsGroupActions(self)
        self.lights = OpenMoticsLights(self)
        self.sensors = OpenMoticsSensors(self)    
        self.shutters = OpenMoticsShutters(self)
        self.thermostats= OpenMoticsThermostats(self)
        
    @property
    def installation_id(self):
        return self._installation_id
    
    @installation_id.setter
    def installation_id(self, installation_id):
        self._installation_id = installation_id

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
        method: str = aiohttp.hdrs.METH_GET, 
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
        if self.token_refresh_method is not None:
            self.token = await self.get_token()

        url = str(URL(f"{self.base_url}/{CLOUD_API_VERSION}{path}"))  

        if self._session is None:
            self._session = aiohttp.ClientSession()
            self._close_session = True

        headers = {
            "Authorization": f"Bearer {self.token}",
            "User-Agent": self.user_agent,
            "Accept": "application/json",
        }

        try:
            async with async_timeout.timeout(self.request_timeout):
                resp = await self._session.request(
                    method,
                    url,
                    headers=headers,
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

    async def get(self, path: str, **kwargs) -> dict[str, Any]:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
            path: path
            **kwargs: extra args

        Returns:
            response json or text
        """
        return await self._request(
            path,
            method = aiohttp.hdrs.METH_GET,
            **kwargs,
        )

    async def post(self, path: str, **kwargs) -> dict[str, Any]:
        """Make get request using the underlying aiohttp.ClientSession.

        Args:
            path: path
            **kwargs: extra args

        Returns:
            response json or text
        """
        return await self._request(
            path,
            method = aiohttp.hdrs.METH_POST,
            **kwargs,
        )

    async def subscribe_webhook(self, installation_id: str, url: str) -> None:
        """Register a webhook with OpenMotics for live updates."""

        # Register webhook
        await self._request(
            "/ws/events",
            method=aiohttp.hdrs.METH_POST,
            data={
                "action": "set_subscription",
                "types": ["OUTPUT_CHANGE", "SHUTTER_CHANGE", "THERMOSTAT_CHANGE", "THERMOSTAT_GROUP_CHANGE" ],
                "installation_ids": [installation_id],
            },
        )

    async def unsubscribe_webhook(self, installation_id: str) -> None:
        """Delete all webhooks for this application ID."""
        await self._request(
            "/ws/events",
            method=aiohttp.hdrs.METH_DELETE,
        )
      
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