"""Module HTTP communication with the OpenMotics API."""

from .localgateway import LocalGateway
from .openmoticscloud import OpenMoticsCloud

__all__ = [
    "OpenMoticsCloud",
    "LocalGateway",
]
