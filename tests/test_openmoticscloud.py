"""Asynchronous Python client for the OpenMotics API."""
# pylint: disable=protected-access
import asyncio
from datetime import date, datetime, time

import aiohttp
import pytest
from aresponses import Response, ResponsesMockServer

from pyhaopenmotics import OpenMoticsCloud
from pyhaopenmotics.errors import (
    OpenMoticsConnectionError,
    OpenMoticsConnectionTimeoutError,
    OpenMoticsError,
)

from . import load_fixtures


@pytest.mark.asyncio
async def test_json_request(aresponses: ResponsesMockServer) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "cloud.openmotics.com",
        "/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with aiohttp.ClientSession() as session:
        omclient = OpenMoticsCloud(token="abc", session=session)  # noqa: S106
        response = await omclient._request("/")
        assert response["status"] == "ok"

@pytest.mark.asyncio
async def test_internal_session(aresponses: ResponsesMockServer) -> None:
    """Test JSON response is handled correctly."""
    aresponses.add(
        "cloud.openmotics.com",
        "/",
        "GET",
        aresponses.Response(
            status=200,
            headers={"Content-Type": "application/json"},
            text='{"status": "ok"}',
        ),
    )
    async with aiohttp.ClientSession() as session:
        omclient = OpenMoticsCloud(token="abc")  # noqa: S106
        response = await omclient._request("/")
        assert response["status"] == "ok"
