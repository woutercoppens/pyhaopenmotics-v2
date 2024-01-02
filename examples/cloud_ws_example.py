#!/usr/bin/env python3
"""Cloud example.

How to use this script:
    export CLIENT_ID="dnfqsdfjqsjfqsdjfqf"
    export CLIENT_SECRET="djfqsdkfjqsdkfjqsdkfjqsdkfjkqsdjfkjdkfqjdskf"
    python cloud_webhooks_example.py

Note:
----
    aiohttp gives an error when tracing ssl via proxy
    https://github.com/aio-libs/aiohttp/issues/6239
    Edit vim ~/.local/lib/python3.11/site-packages/aiohttp/connector.py (line 1212)
    runtime_has_start_tls = False if req.proxy.scheme != "https" else self._loop_supports_start_tls()

"""
from __future__ import annotations

import asyncio
import logging
import os

from aiohttp import ClientSession

try:
    from dotenv import load_dotenv
except ModuleNotFoundError as exc:
    msg = "You have to run 'pip install python-dotenv' first"
    raise ImportError(msg) from exc

try:
    from authlib.integrations.httpx_client import AsyncOAuth2Client
except ModuleNotFoundError as exc:
    msg = "You have to run 'pip install httpx authlib' first"
    raise ImportError(msg) from exc


from pyhaopenmotics import OpenMoticsCloud, WebsocketClient
from pyhaopenmotics.client.const import CLOUD_SCOPE, OAUTH2_TOKEN
from pyhaopenmotics.helpers.aiohttp_trace import request_tracer

# UNCOMMENT THIS TO SEE ALL THE HTTPX INTERNAL LOGGING
log = logging.getLogger()
log.setLevel(logging.DEBUG)
log_format = logging.Formatter("[%(asctime)s] [%(levelname)s] - %(message)s")
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(log_format)
log.addHandler(console)


load_dotenv()

client_id = os.environ["CLIENT_ID"]
client_secret = os.environ["CLIENT_SECRET"]

httpx_headers = {
    # "User-Agent": self.user_agent,
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, defalte, br",
    "Referer": "https://portal.openmotics.com",
    "Content-Type": "application/json",
    "Origin": "https://portal.openmotics.com",
    "Connection": "keep-alive",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
}


async def main() -> None:
    """Docstring."""
    token = None
    trace = {}

    async with ClientSession(
        trust_env=True,
        trace_configs=[request_tracer(trace)],
    ) as session:
        async with session.get("https://portal.openmotics.com") as resp:
            print(resp.status)

    async with AsyncOAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        token_endpoint_auth_method="client_secret_post",  # noqa: S106 # nosec
        scope=CLOUD_SCOPE,
        token_endpoint=OAUTH2_TOKEN,
        grant_type="client_credentials",
        headers=httpx_headers,
    ) as httpx_session:
        token = await httpx_session.fetch_token(
            url=OAUTH2_TOKEN,
            grant_type="client_credentials",
        )
        access_token = token.get("access_token")

        omclient = OpenMoticsCloud(
            token=access_token,
            session=ClientSession(
                trust_env=True,
                trace_configs=[request_tracer(trace)],
            ),
        )

        await omclient.get("/")

        installations = await omclient.installations.get_all()
        i_id = installations[0].idx

        await omclient.installations.get_by_id(i_id)
        omclient.installation_id = i_id

        await omclient.outputs.get_all()
        print(trace)

        ws_client = WebsocketClient(omclient)

        await ws_client.connect()

        await ws_client.close()


if __name__ == "__main__":
    asyncio.run(main())
