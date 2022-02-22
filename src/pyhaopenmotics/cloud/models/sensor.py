"""Sensor Model for the OpenMotics API."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field


class FloorCoordinates(BaseModel):
    """Class holding the floor_coordinates."""

    x: Optional[int] = None
    y: Optional[int] = None


class Location(BaseModel):
    """Class holding the location."""

    floor_coordinates: Optional[FloorCoordinates] = None
    floor_id: Optional[int] = None
    installation_id: Optional[int] = None
    room_id: Optional[int] = None


class Status(BaseModel):
    """Class holding the status."""

    humidity: Optional[float] = None
    temperature: Optional[float] = None
    brightness: Optional[int] = None


class Sensor(BaseModel):
    """Class holding an OpenMotics Output.

    # noqa: E800
    #     {
    #     "_version": <version>,
    #     "id": <id>,
    #     "name": "<name>",
    #     "location": {
    #         "room_id": null | <room_id>,
    #         "installation_id": <installation id>
    #     },
    #     "status": {
    #         "humidity": null | <hunidity 0 - 100>,
    #         "temperature": null | <temperature -32 - 95>,
    #         "brightness": null | <brightness 0 - 100>
    #     }
    # }
     #     ...
    """

    # pylint: disable=too-many-instance-attributes
    idx: int = Field(..., alias="id")
    local_id: Optional[int] = None
    name: Optional[str] = None
    location: Optional[Location] = None
    physical_quantity: Optional[str]
    status: Optional[Status] = None
    last_state_change: Optional[float] = None
    version: Optional[str] = Field(None, alias="_version")

    def __str__(self):
        """Represent the class objects as a string.

        Returns:
            string

        """
        return f"{self.idx}_{self.name}"
