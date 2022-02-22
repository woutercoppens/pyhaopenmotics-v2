"""Asynchronous client for the OpenMotics API."""
# pylint: disable=protected-access
import asyncio
from datetime import datetime

import httpx
import pytest
from authlib.integrations.base_client.errors import MissingTokenError
from respx import MockRouter

from pyhaopenmotics import CloudClient
from pyhaopenmotics.errors import ApiException, RequestUnauthorizedException

get_token_data_request = {
    "grant_type": "client_credentials",
    "client_id": "abc",
    "client_secret": "abc",
}

get_installations_data_request = {
    "access_token": "12345",
}


@pytest.mark.asyncio
class TestOpenMotics:
    async def test_async_get_token__invalid_request_params__raises_error(
        self, respx_mock: MockRouter
    ):
        respx_mock.post(
            "https://cloud.openmotics.com/api/v1/authentication/oauth2/token",
            data=get_token_data_request,
        ).respond(400)

        async with CloudClient(
            client_id="abc",
            client_secret="abc",
        ) as client:
            with pytest.raises(ApiException):
                await client.get_token()

    async def test_async_get_installations_data__missing_token_params__raises_error(
        self, respx_mock: MockRouter
    ):
        respx_mock.get(
            "https://cloud.openmotics.com/api/v1/base/installations",
            data=get_installations_data_request,
        ).respond(400)

        async with CloudClient(
            client_id="abc",
            client_secret="abc",
        ) as client:
            with pytest.raises(MissingTokenError):
                await client.installations.get_all()
