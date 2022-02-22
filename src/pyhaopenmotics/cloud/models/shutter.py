"""Output Model for the OpenMotics API."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class FloorCoordinates(BaseModel):
    """Class holding the floor_coordinates."""

    x: Optional[int] = None
    y: Optional[int] = None


class Location(BaseModel):
    """Class holding the location."""

    floor_coordinates: Optional[FloorCoordinates] = None
    installation_id: Optional[int] = None
    floor_id: Optional[int] = None
    gateway_id: Optional[int] = None
    room_id: Optional[int] = None


class Status(BaseModel):
    """Class holding the status."""

    locked: Optional[bool] = None
    manual_override: Optional[bool] = None
    state: Optional[str] = None
    position: Optional[int] = None
    last_change: Optional[float] = None
    preset_position: Optional[int] = None


class Attributes(BaseModel):
    """Class holding the attributes."""

    azimuth: Optional[str] = None
    compass_point: Optional[str] = None
    surface_area: Optional[str] = None


class Shutter(BaseModel):
    """Object holding an OpenMotics Shutter.

    # noqa: E800
    # {
    # "_version": <version>,
    # "configuration": {
    #     "group_1": null | <group id>,
    #     "group_2": null | <group id>,
    #     "name": "<name>",
    #     "steps": null | <number of steps>,
    #     "timer_down": <timer down>,
    #     "timer_up": <timer up>,
    #     "up_down_config": <up down configuration>
    # },
    # "id": <id>,
    # "capabilities": ["UP_DOWN", "POSITION", "RELATIVE_POSITION",
    #          "HW_LOCK"|"CLOUD_LOCK", "PRESET", "CHANGE_PRESET"],
    # "location": {
    #     "floor_coordinates": {
    #         "x": null | <x coordinate>,
    #         "y": null | <y coordinate>
    #     },
    #     "floor_id": null | <floor id>,
    #     "installation_id": <installation id>,
    #     "room_id": null | <room_id>
    # },
    # "name": "<name>",
    # "status": {
    #     "last_change": <epoch in seconds>
    #     "position": null | <position>,
    #     "state": null | "UP|DOWN|STOP|GOING_UP|GOING_DOWN",
    #     "locked": true | false,
    #     "manual_override": true | false
    # }
    # }
    """

    # pylint: disable=too-many-instance-attributes
    idx: int = Field(..., alias="id")
    local_id: Optional[int] = None
    name: Optional[str] = None
    shutter_type: str = Field(None, alias="type")
    capabilities: Optional[dict] = None
    status: Optional[Status] = None
    location: Optional[Location] = None
    attributes: Optional[Attributes] = None
    metadata: Optional[str] = None
    version: Optional[str] = Field(None, alias="_version")

    def __str__(self):
        """Represent the class objects as a string.

        Returns:
            string

        """
        return f"{self.idx}_{self.name}"
