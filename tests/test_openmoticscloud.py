"""Asynchronous client for the OpenMotics API."""
# flake8: noqa
# pylint: disable=protected-access
# # mypy: ignore-errors
import asyncio

import aiohttp
import pytest

from pyhaopenmotics import OpenMoticsCloud
from pyhaopenmotics.const import CLOUD_API_VERSION, CLOUD_BASE_URL
from pyhaopenmotics.errors import OpenMoticsConnectionError, OpenMoticsError

get_token_data_request = {
    "grant_type": "client_credentials",
    "client_id": "abc",
    "client_secret": "abc",
}

get_installations_data_request = {
    "access_token": "12345",
}


# @pytest.mark.asyncio
# async def test_json_request(aresponses) -> None:
#     """Test JSON response is handled correctly."""
#     aresponses.add(
#         CLOUD_BASE_URL,
#         CLOUD_API_VERSION,
#         "GET",
#         aresponses.Response(
#             status=200,
#             headers={"Content-Type": "application/json"},
#             text='{"_error": None}',
#         ),
#     )
#     async with aiohttp.ClientSession() as session:
#         open_motics = OpenMoticsCloud(session=session, token='12345') # noqa: S106
#         response = await open_motics._request("/")
#         print(response)
#         assert response["_error"] is None


# @pytest.mark.asyncio
# async def test_internal_session(aresponses) -> None:
#     """Test JSON response is handled correctly."""
#     aresponses.add(
#         CLOUD_BASE_URL,
#         CLOUD_API_VERSION,
#         "GET",
#         aresponses.Response(
#             status=200,
#             headers={"Content-Type": "application/json"},
#             text='{"status": "ok"}',
#         ),
#     )
#     async with OpenMoticsCloud(token='12345') as open_motics: # noqa: S106
#         response = await open_motics._request("/")
#         assert response["status"] == "ok"


@pytest.mark.asyncio
async def test_timeout(aresponses) -> None:  # type: ignore
    """Test request timeout."""
    # Faking a timeout by sleeping
    async def response_handler(_):  # type: ignore
        await asyncio.sleep(2)
        return aresponses.Response(body="Goodmorning!")

    aresponses.add(CLOUD_BASE_URL, CLOUD_API_VERSION, "POST", response_handler)

    async with aiohttp.ClientSession() as session:
        open_motics = OpenMoticsCloud(
            session=session,
            token="12345",  # noqa: S106
            request_timeout=1,
        )
        with pytest.raises(OpenMoticsConnectionError):
            assert await open_motics._request("/")


@pytest.mark.asyncio
async def test_http_error400(aresponses) -> None:  # type: ignore
    """Test HTTP 404 response handling."""
    aresponses.add(
        CLOUD_BASE_URL,
        CLOUD_API_VERSION,
        "GET",
        aresponses.Response(text="OMG PUPPIES!", status=404),
    )

    async with aiohttp.ClientSession() as session:
        open_motics = OpenMoticsCloud(session=session, token="12345")  # noqa: S106
        with pytest.raises(OpenMoticsError):
            assert await open_motics._request("/")


@pytest.mark.asyncio
async def test_http_error500(aresponses) -> None:  # type: ignore
    """Test HTTP 500 response handling."""
    aresponses.add(
        CLOUD_BASE_URL,
        CLOUD_API_VERSION,
        "GET",
        aresponses.Response(
            body=b'{"status":"nok"}',
            status=500,
            headers={"Content-Type": "application/json"},
        ),
    )

    async with aiohttp.ClientSession() as session:
        open_motics = OpenMoticsCloud(session=session, token="12345")  # noqa: S106
        with pytest.raises(OpenMoticsError):
            assert await open_motics._request("/")
