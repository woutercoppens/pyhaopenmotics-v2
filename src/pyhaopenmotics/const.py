"""Asynchronous Python client for the OpenMotics API."""
from __future__ import annotations

CLOUD_BASE_URL = "https://cloud.openmotics.com/api"
CLOUD_API_VERSION = "v1.1"
CLOUD_API_TOKEN_URL = "/authentication/oauth2/token"  # noqa # nosec
CLOUD_API_AUTHORIZATION_URL = "/authentication/oauth2/authorize"

# noqa: E800
# SCOPE = "configure.event_rules view view.energy.realtime configure.outputs configure view.sensors control view.thermostats control.ventilation view.energy configure.thermostats view.outputs view.event_rules control.thermostats view.energy.reports control.outputs view.installations"
SCOPE = "control view configure"
