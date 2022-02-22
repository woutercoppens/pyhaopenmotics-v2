"""Module HTTP communication with the OpenMotics API."""

from .errors import (
    ApiException,
    NetworkException,
    NetworkTimeoutException,
    NonOkResponseException,
    NonRetryableException,
    RequestBackoffException,
    RequestClientException,
    RequestException,
    RequestServerException,
    RequestUnauthorizedException,
    RetryableException,
    UnsuportedArgumentsException,
)
from .localgateway import LocalGateway
from .openmoticscloud import OpenMoticsCloud

# from .auth import OpenMoticsCloudSession

__all__ = [
    "OpenMoticsCloud",
    "LocalGateway",
    "ApiException",
    "NonOkResponseException",
    "NetworkException",
    "NetworkTimeoutException",
    "NonRetryableException",
    "RequestBackoffException",
    "RequestClientException",
    "RequestException",
    "RequestServerException",
    "RequestUnauthorizedException",
    "RetryableException",
    "UnsuportedArgumentsException",
]
