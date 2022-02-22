"""Thermostat Model for the OpenMotics API."""
from __future__ import annotations
from lib2to3.pgen2.token import OP
from statistics import mode

from typing import List, Optional

from pydantic import BaseModel, Field


class FloorCoordinates(BaseModel):
    """Class holding the floor_coordinates."""

    x: Optional[int] = None
    y: Optional[int] = None


class GroupLocation(BaseModel):
    """Class holding the location."""

    floor_coordinates: Optional[FloorCoordinates] = None
    floor_id: Optional[int] = None
    installation_id: Optional[int] = None
    room_id: Optional[int] = None

class UnitLocation(BaseModel):
    """Class holding the location."""

    thermostat_group_id: Optional[int] = None
    installation_id: Optional[int] = None
    room_id: Optional[int] = None

class GroupStatus(BaseModel):
    """Class holding the status."""

    mode: Optional[str] = None
    state: Optional[bool] = None

class UnitStatus(BaseModel):
    """Class holding the status."""

    actual_temperature: Optional[float] = None
    current_setpoint: Optional[float] = None
    output_0: Optional[str] = None
    output_1: Optional[str] = None
    preset: Optional[str] = None

class Presets(BaseModel):
    """Class holding the status."""

    away: Optional[str] = None
    party: Optional[str] = None
    vacation: Optional[str] = None

class Schedule(BaseModel):
    """Class holding the schedule."""

    data: Optional[dict] = None
    start: Optional[str] = None


class ConfigurationPreset(BaseModel):
    """Class holding the configuration presets."""

    output_0_id: Optional[int] = None
    output_1_id: Optional[int] = None
    presets: Optional[Presets] = None
    schedule: Optional[Schedule] = None
    sensor_id: Optional[int] = None

class Configuration(BaseModel):
    """Class holding the configuration."""

    heating: Optional[ConfigurationPreset] = None
    cooling: Optional[ConfigurationPreset] = None


class Allowed(BaseModel):
    """Object holding allowed."""

    allowed: Optional[bool] = None


class Acl(BaseModel):
    """Object holding an acl."""

    set_state: Optional[Allowed] = None
    set_mode: Optional[Allowed] = None


class ThermostatGroup(BaseModel):
    """Class holding an OpenMotics ThermostatGroup .

    # noqa: E800
#  {
#     "_acl": <acl>,
#     "_version": <version>,
#     "schedule": {
#         "<optional timestamp>": "AUTO|AWAY|PARTY|VACATION",
#         ...
#     },
#     "status": {
#         "mode": "HEATING|COOLING",
#         "state": "ON|OFF"
#     },
#     "capabilities": ["HEATING", "COOLING"]
# }

    """

    # pylint: disable=too-many-instance-attributes
    idx: int = Field(..., alias="id")
    local_id: int
    name: Optional[str] = None
    location: Optional[GroupLocation] = None
    status: Optional[GroupStatus] = None
    version: Optional[str] = Field(None, alias="_version")
    acl: Optional[Acl] = Field(None, alias="_acl")
    thermostat_ids: Optional[dict] = None
    schedule: Optional[Schedule] = None

    def __str__(self):
        """Represent the class objects as a string.

        Returns:
            string

        """
        return f"{self.idx}_{self.name}"

class ThermostatUnit(BaseModel):
    """Class holding an OpenMotics ThermostatGroup .

    # noqa: E800
    # {
    #     "_version": <version>,
    #     "configuration": {
    #         "heating": {
    #             "output_0_id": <first output id>,
    #             "output_1_id": null | <second output id>,
    #             "presets": {`
    #                 "AWAY": <away temperature>,
    #                 "PARTY": <party temperature>,
    #                 "VACATION": <vacation temperature>
    #             },
    #             "schedule": {
    #                 "data": [
    #                     {
    #                         "0": <temperature from this timestamp>,
    #                         "23400": <temperature from this timestamp>,
    #                         "30600": <temperature from this timestamp>,
    #                         "61200": <temperature from this timestamp>,
    #                         "84600": <temperature from this timestamp>
    #                     },
    #                     ...
    #                 ],
    #                 "start": <timestamp on which schedule needs to be based>
    #             },
    #             "sensor_id": <room sensor id>
    #         },
    #         "cooling": {
    #             "output_0_id": <first output id>,
    #             "output_1_id": null | <second output id>,
    #             "presets": {
    #                 "AWAY": <away temperature>,
    #                 "PARTY": <party temperature>,
    #                 "VACATION": <vacation temperature>
    #             },
    #             "schedule": {
    #                 "data": [
    #                     {
    #                         "0": <temperature from this timestamp>,
    #                         "23400": <temperature from this timestamp>,
    #                         "30600": <temperature from this timestamp>,
    #                         "61200": <temperature from this timestamp>,
    #                         "84600": <temperature from this timestamp>
    #                     },
    #                     ...
    #                 ],
    #                 "start": <timestamp on which schedule needs to be based>
    #             },
    #             "sensor_id": <room sensor id>
    #         }
    #     },
    #     "id": <id>,
    #     "location": {
    #         "installation_id": <installation id>,
    #         "room_id": null | <room id>,
    #         "thermostat_group_id": <thermostat group id>
    #     },
    #     "name": "<name>",
    #     "status": {
    #         "actual_temperature": <current measured temperature>,
    #         "current_setpoint": <desired temperature>,
    #         "output_0": <level of first output>,
    #         "output_1": <level of second output>,
    #         "preset": "AUTO|PARTY|AWAY|VACATION"
    #     }
    # }
    """
    # pylint: disable=too-many-instance-attributes
    idx: int = Field(..., alias="id")
    local_id: Optional[int] = None
    name: Optional[str] = None
    location: Optional[UnitLocation] = None
    status: Optional[UnitStatus] = None
    version: Optional[str] = Field(None, alias="_version")
    acl: Optional[str] = Field(None, alias="_acl")

    def __str__(self):
        """Represent the class objects as a string.

        Returns:
            string

        """
        return f"{self.idx}_{self.name}"
