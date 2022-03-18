"""Module containing the base of an groupaction."""
from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any, Optional

from pyhaopenmotics.helpers import merge_dicts
from .models.groupaction import GroupAction

if TYPE_CHECKING:
    from pyhaopenmotics.localgateway import LocalGateway  # pylint: disable=R0401

class OpenMoticsGroupActions:  # noqa: SIM119
    """Object holding information of the OpenMotics groupactions.

    All actions related to groupaction or a specific groupaction.
    """

    def __init__(self, omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
            omcloud: LocalGateway
        """
        self._omcloud = omcloud
    #     self._groupaction_configs: list[Any] = []

    # @property
    # def groupaction_configs(self) -> list[Any]:
    #     """Get a list of all groupaction confs.

    #     Returns:
    #         list of all groupaction confs
    #     """
    #     return self._groupaction_configs

    # @groupaction_configs.setter
    # def groupaction_configs(self, groupaction_configs: list[Any]) -> None:
    #     """Set a list of all groupaction confs.

    #     Args:
    #         groupaction_configs: list
    #     """
    #     self._groupaction_configs = groupaction_configs


    async def get_all(
        self,
        groupaction_filter: str | None = None,
    ) -> list[GroupAction]:
        """Call lists all GroupAction objects.

        Args:
            groupaction_filter: Optional filter

        Returns:
            list with all groupactions

        usage: The usage filter allows the GroupActions to be filtered for
            their intended usage.
            SCENE: These GroupActions can be considered a scene,
                e.g. watching tv or romantic dinner.
        # noqa: E800
        # [{
        #      "_version": <version>,
        #      "actions": [
        #          <action type>, <action number>,
        #          <action type>, <action number>,
        #          ...
        #      ],
        #  "id": <id>,
        #  "location": {
        #      "installation_id": <installation id>
        #  },
        #  "name": "<name>"
        #  }
        """
        # if len(self.groupaction_configs) == 0:
        #     goc = await self._omcloud.exec_action("get_groupaction_configurations")
        #     if goc["success"] is True:
        #         self.groupaction_configs = goc["config"]

        # groupactions_status = await self._omcloud.exec_action("get_groupaction_status")
        # status = groupactions_status["status"]

        # data = merge_dicts(self.groupaction_configs, "status", status)

        data = await self._omcloud.exec_action("get_group_action_configurations")

        groupactions = [GroupAction.from_dict(device) for device in data["config"]]

        if groupaction_filter is not None:
            # implemented later
            pass

        return groupactions  # type: ignore


    async def get_by_id(
        self,
        groupaction_id: int,
    ) -> Optional[GroupAction]:
        """Get a specified groupaction object.

        Args:
            groupaction_id: int

        Returns:
            Returns a groupaction with id
        """
        for groupaction in await self.get_all():
            if groupaction.idx == groupaction_id:
                return groupaction
        return None

    async def trigger(
        self,
        groupaction_id: int,
    ) -> Any:
        """Trigger a specified groupaction object.

        Args:
            groupaction_id: int

        Returns:
            Returns a groupaction with id
        """
        data = {"group_action_id": groupaction_id}
        return await self._omcloud.exec_action("do_group_action", data=data)

    async def by_usage(
        self,
        groupaction_usage: str,
    ) -> list[GroupAction]:
        """Return a specified groupaction object.

        The usage filter allows the GroupActions to be filtered for their
        intended usage.

        Args:
            groupaction_usage: str

        Returns:
            Returns a groupaction with id
        """
        groupaction_list = []
        for groupaction in await self.get_all():
            if groupaction.name == groupaction_usage:
                groupaction_list.append(groupaction)
        return groupaction_list      


    async def scenes(self) -> Any:
        """Return all scenes object.

        SCENE: These GroupActions can be considered a scene,
            e.g. watching tv or romantic dinner.

        Returns:
            Returns all scenes
        """
        if (response := await self.by_usage("SCENE")) is None:
            return None
        return response
