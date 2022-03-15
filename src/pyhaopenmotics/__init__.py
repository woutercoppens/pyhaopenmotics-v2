"""Module HTTP communication with the OpenMotics API."""

from .errors import (
    OpenMoticsConnectionError,
    OpenMoticsConnectionTimeoutError,
    OpenMoticsError,
)
from .localgateway import LocalGateway
from .openmoticscloud import OpenMoticsCloud

from .cloud.models import Installation

__all__ = [
    "OpenMoticsCloud",
    "LocalGateway",
    "OpenMoticsError",
    "OpenMoticsConnectionError",
    "OpenMoticsConnectionTimeoutError",
    "Installation",
]
