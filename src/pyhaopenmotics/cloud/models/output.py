"""Output Model for the OpenMotics API."""
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
    installation_id: Optional[int] = None
    gateway_id: Optional[int] = None
    floor_id: Optional[int] = None
    room_id: Optional[int] = None


class Status(BaseModel):
    """Class holding the status."""

    on: bool
    locked: Optional[bool] = None
    manual_override: Optional[bool] = None
    value: Optional[int] = None


class Output(BaseModel):
    """Class holding an OpenMotics Output.

    # noqa: E800
     # [{
     #     'name': 'name1',
     #     'type': 'OUTLET',
     #     'capabilities': ['ON_OFF'],
     #     'location': {'floor_coordinates': {'x': None, 'y': None},
     #          'installation_id': 21,
     #          'gateway_id': 408,
     #          'floor_id': None,
     #          'room_id': None},
     #     'metadata': None,
     #     'status': {'on': False, 'locked': False, 'manual_override': False},
     #     'last_state_change': 1633099611.275243,
     #     'id': 18,
     #     '_version': 1.0
     #     },{
     #     'name': 'name2',
     #     'type': 'OUTLET',
     #     ...
    """

    # pylint: disable=too-many-instance-attributes
    idx: int = Field(..., alias="id")
    local_id: Optional[int] = None
    name: Optional[str] = None
    output_type: str = Field(None, alias="type")
    location: Optional[Location] = None
    capabilities: Optional[List] = None
    metadata: Optional[dict] = None
    status: Optional[Status] = None
    last_state_change: Optional[float] = None
    version: Optional[str] = Field(None, alias="_version")

    _brightness: Optional[int] = None

    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns:
            string

        """
        return f"{self.idx}_{self.name}_{self.output_type}"
