#!/usr/bin/env python3
# noqa: E800

"""
Cloud example.

How to use this script:
    export CLIENT_ID="dnfqsdfjqsjfqsdjfqf"
    export CLIENT_SECRET="djfqsdkfjqsdkfjqsdkfjqsdkfjkqsdjfkjdkfqjdskf"
    python cloud_example.py
"""
import asyncio
# import imp
import aiohttp
import logging
import os
from yarl import URL

try:
    from dotenv import load_dotenv
except ModuleNotFoundError as exc:
    raise ImportError("You have to run 'pip install python-dotenv' first") from exc

try:
    from authlib.integrations.httpx_client import (  # type: ignore
        AsyncOAuth2Client,
        OAuthError,
    )
except ModuleNotFoundError as exc:
    raise ImportError("You have to run 'pip install authlib' first") from exc

from oauthlib.oauth2 import BackendApplicationClient
from pyhaopenmotics import OpenMoticsCloud
from pyhaopenmotics.const import (
    CLOUD_API_VERSION,
    CLOUD_API_TOKEN_URL,
    CLOUD_API_AUTHORIZATION_URL,
    SCOPE,
)

import aiohttp

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

token_url = 'https://cloud.openmotics.com:443/api/v1/authentication/oauth2/token'
authorize_url = 'https://cloud.openmotics.com:443/api/v1/authentication/oauth2/authorize'
base_url = 'https://cloud.openmotics.com:443/api/v1'

async def main():
    token = None

    client = BackendApplicationClient(client_id=client_id)
    async with AsyncOAuth2Client(
        client_id=client_id,
        client_secret=client_secret,
        token_endpoint_auth_method="client_secret_post",  # nosec
        scope=SCOPE,
        token_endpoint=token_url,
        grant_type="client_credentials",
        # update_token=self.token_saver,
        ) as httpx_session:
        token = await async_get_token(httpx_session)
        await async_call_api(token)

async def async_get_token(httpx_session):
    tkn = await httpx_session.fetch_token(
                url=token_url,
                grant_type="client_credentials",
            )
    token = tkn.get('access_token')
    print(token)
    return token

async def async_call_api(token):
    print(f"async_call_api: {token}")
 
    omclient = OpenMoticsCloud(
        token = token)

    installations = await omclient.installations.get_all()
    print(installations)

    i_id = installations[0].idx

    installation = await omclient.installations.get_by_id(i_id)
    print(installation)
    omclient.installation_id = i_id
    # print(installation.idx)
    # print(installation.name)

    outputs = await omclient.outputs.get_all()
    print(outputs)

    print(outputs[0])

    sensors = await omclient.sensors.get_all()
    print(sensors)

    ga = await omclient.groupactions.get_all()
    print(ga)

    tg = await omclient.thermostats.groups.get_all()
    print(tg)

    tu = await omclient.thermostats.units.get_all()
    print(tu)

    await omclient.close()


if __name__ == "__main__":
    asyncio.run(main())
