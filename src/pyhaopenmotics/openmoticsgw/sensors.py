"""Module containing the base of an output."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from pyhaopenmotics.helpers import merge_dicts
from pyhaopenmotics.openmoticsgw.models.sensor import Sensor

if TYPE_CHECKING:
    from pyhaopenmotics.localgateway import LocalGateway  # pylint: disable=R0401


class OpenMoticsSensors:  # noqa: SIM119
    """Object holding information of the OpenMotics sensors.

    All actions related to Sensors or a specific Sensor.
    """

    def __init__(self, omcloud: LocalGateway) -> None:
        """Init the installations object.

        Args:
            omcloud: LocalGateway
        """
        self._omcloud = omcloud
        self._sensor_configs: list[Any] =[]

    @property
    def sensor_configs(self) -> list[Any]:
        """Get a list of all sensor confs.

        Returns:
            list of all sensor confs
        """
        return self._sensor_configs

    @sensor_configs.setter
    def sensor_configs(self, sensor_configs: list[Any]) -> None:
        """Set a list of all sensor confs.

        Args:
            sensor_configs: list
        """
        self._sensor_configs = sensor_configs

    async def get_all(  # noqa: A003
        self,
        sensor_filter: str | None = None,
    ) -> list[Sensor]: 
        """Get a list of all sensor objects.

        Args:
            sensor_filter: str

        Returns:
            Dict with all sensors
        """
        if len(self.sensor_configs) == 0:
            goc = await self._omcloud.exec_action("get_sensor_configurations")
            if goc["success"] is True:
                self.sensor_configs = goc["config"]

        sensor_brightness_status = await self._omcloud.exec_action("get_sensor_brightness_status")
        brightness_status = sensor_brightness_status["status"]
        print(brightness_status)
        sensor_humidity_status = await self._omcloud.exec_action("get_sensor_humidity_status")
        humidity_status = sensor_humidity_status["status"]
        sensor_temperature_status = await self._omcloud.exec_action("get_sensor_temperature_status")
        temperature_status = sensor_temperature_status["status"]

        data0 = merge_dicts(self.sensor_configs, "status", brightness_status)
        data1 = merge_dicts(data0, "status", humidity_status)
        data = merge_dicts(data1, "status", temperature_status)

        sensors = [Sensor.from_dict(device) for device in data]
        
        if sensor_filter is not None:
            # implemented later
            pass

        return sensors # type: ignore

    async def get_by_id(
        self,
        sensor_id: int,
    ) -> Sensor:
        """Get sensor by id.

        Args:
            sensor_id: int

        Returns:
            Returns a sensor with id
        """
        # result: Sensor = None
        for sensor in await self.get_all():
            if sensor.idx == sensor_id: 
                result = sensor

        return result 