"""Module containing the base of an light."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

from pyhaopenmotics.helpers import merge_dicts

from .models.light import Light

if TYPE_CHECKING:
    from pyhaopenmotics.localgateway import LocalGateway  # pylint: disable=R0401


@dataclass
class OpenMoticsLights:  # noqa: SIM119
    """Object holding information of the OpenMotics lights.

    All actions related to lights or a specific light.
    """

    def __init__(self, omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
            omcloud: LocalGateway
        """
        self._omcloud = omcloud
        self._light_configs: list[Any] = []

    @property
    def light_configs(self) -> list[Any]:
        """Get a list of all light confs.

        Returns:
            list of all light confs
        """
        return self._light_configs

    @light_configs.setter
    def light_configs(self, light_configs: list[Any]) -> None:
        """Set a list of all light confs.

        Args:
            light_configs: list
        """
        self._light_configs = light_configs

    async def get_all(  # noqa: A003
        self,
        light_filter: str | None = None,
    ) -> list[Optional[Light]]:
        """Get a list of all light objects.

        Args:
            light_filter: str

        Returns:
            list with all lights
        """

        if light_filter is not None:
            # implemented later
            pass

        return [] 

    async def get_by_id(
        self,
        light_id: int,
    ) -> Optional[Light]:
        """Get light by id.

        Args:
            light_id: int

        Returns:
            Returns a light with id
        """
        if light_id is not None:
            # implemented later
            pass

        return None 

    async def toggle(
        self,
        light_id: int,
    ) -> Any:
        """Toggle a specified light object.

        Args:
            light_id: int

        Returns:
            Returns a light with id
        """
        if light_id is not None:
            # implemented later
            pass

        return None 

    async def turn_on(
        self,
        light_id: int,
        value: int | None = 100,
    ) -> Any:
        """Turn on a specified light object.

        Args:
            light_id: int
            value: <0 - 100>

        Returns:
            Returns a light with id
        """
        if light_id is not None:
            # implemented later
            pass

        return None 

    async def turn_off(
        self,
        light_id: int,
    ) -> Any:
        """Turn off a specified light object.

        Args:
            light_id: int

        Returns:
            Returns a light with id
        """
        if light_id is not None:
            # implemented later
            pass

        return None