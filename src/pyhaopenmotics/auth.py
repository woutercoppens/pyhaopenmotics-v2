"""Module containing an AuthClient for the OpenMotics API."""

from __future__ import annotations

import logging

from contextlib import asynccontextmanager
from typing import AsyncGenerator, Callable
import aiohttp
import asyncio

from oauthlib.oauth2 import BackendApplicationClient, WebApplicationClient
from async_oauthlib import OAuth2Session
from oauthlib.oauth2 import OAuth2Token
from yarl import URL

from .const import (
    CLOUD_API_BASE_PATH,
    CLOUD_API_HOST,
    CLOUD_API_PORT,
    CLOUD_API_VERSION,
    CLOUD_API_TOKEN_URL,
    CLOUD_API_AUTHORIZATION_URL,
    SCOPE,
)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def auth_client(
    client_id: str,
    client_secret: str,
    on_token_update: Callable[[Token], None],
) -> AsyncGenerator[OpenMoticsCloudSession, None]:
    
    c = OpenMoticsCloudSession(client_id, client_secret)

    try:
        yield c
    finally:
        await client.aclose()

async def on_request_start(session, context, params):
    logging.getLogger('aiohttp.client').debug(f'Starting request <{params}>')
    print("Starting %s request for %s. I sent: %s" % (params.method, params.url, params.headers))

async def on_request_end(session, trace_config_ctx, params):
    print("Ending %s request for %s. I sent: %s" % (params.method, params.url, params.headers))
    print('Sent headers: %s' % params.response.request_info.headers)

class OpenMoticsCloudSession():

    _close_session: bool = False

    def __init__(
        self,
        client_id: str,
        client_secret: str,
    ) -> None:
        self.token = None
        self.client_id = client_id
        self.client_secret = client_secret

        self.scope = SCOPE
        extra = {'client_id': self.client_id,
                 'client_secret': self.client_secret}

        client = BackendApplicationClient(client_id=self.client_id)
        client.prepare_request_body(scope=self.scope) 

        self.token_url = str(URL(f"https://{CLOUD_API_HOST}:{CLOUD_API_PORT}{CLOUD_API_BASE_PATH}{CLOUD_API_VERSION}{CLOUD_API_TOKEN_URL}"))  
        self.authorization_url = str(URL(f"https://{CLOUD_API_HOST}:{CLOUD_API_PORT}{CLOUD_API_BASE_PATH}{CLOUD_API_VERSION}{CLOUD_API_AUTHORIZATION_URL}"))  

        logging.basicConfig(level=logging.DEBUG)
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(on_request_start)
        trace_config.on_request_end.append(on_request_end)     

        self._session = OAuth2Session(
            client_id = self.client_id,
            client = client,
            auto_refresh_url = self.token_url,
            scope = self.scope,
            auto_refresh_kwargs=extra,
            raise_for_status = True,
            trace_configs=[trace_config],
        )
        self._close_session = True

    async def get_token(self):
        self.token = await self._session.fetch_token(
            token_url=self.token_url, 
            client_id=self.client_id, 
            client_secret=self.client_secret,
        )
        return self.token

    async def token_saver(self, token):
        self.token = token

    # async def token(self):
    #     return self.token 

    def get_session(self):
        return self._session


    async def close(self) -> None:
        """Close open client session."""
        if self._session and self._close_session:
            await self._session.close()

    async def __aenter__(self) -> Toon:
        """Async enter."""
        return self

    async def __aexit__(self, *exc_info) -> None:
        """Async exit."""
        await self.close()