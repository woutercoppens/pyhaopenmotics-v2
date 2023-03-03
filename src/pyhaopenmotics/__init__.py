"""Module HTTP communication with the OpenMotics API."""

from pyhaopenmotics.client.errors import (
    AuthenticationException,
    OpenMoticsConnectionError,
    OpenMoticsConnectionSslError,
    OpenMoticsConnectionTimeoutError,
    OpenMoticsError,
)
from pyhaopenmotics.client.localgateway import LocalGateway
from pyhaopenmotics.client.openmoticscloud import OpenMoticsCloud
from pyhaopenmotics.cloud.models import Installation
from pyhaopenmotics.helpers import get_ssl_context

__all__ = [
    "OpenMoticsCloud",
    "LocalGateway",
    "OpenMoticsError",
    "OpenMoticsConnectionError",
    "OpenMoticsConnectionTimeoutError",
    "OpenMoticsConnectionSslError",
    "AuthenticationException",
    "Installation",
    "get_ssl_context",
]
