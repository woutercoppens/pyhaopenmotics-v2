"""Output Model for the OpenMotics API."""
from __future__ import annotations

from typing import List, Optional

from dataclasses import dataclass
from enum import Enum

from .const import OPENMOTICS_OUTPUT_TYPE_TO_NAME

@dataclass
class FloorCoordinates:
    """Class holding the floor_coordinates."""

    x: int
    y: int

    @staticmethod
    def from_dict(data: dict[str, Any]) -> FloorCoordinates:

        return FloorCoordinates(
            x = data.get('x', 0),
            y = data.get('y', 0),
        )

@dataclass
class Location:
    """Class holding the location."""

    floor_coordinates: FloorCoordinates 
    installation_id: int | None
    gateway_id: int | None
    floor_id: int | None
    room_id: int | None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Location:

        _floor_coordinates: FloorCoordinates = None
        if data is not None:
            if 'floor_coordinates' in data:
                _floor_coordinates = FloorCoordinates.from_dict(data.get('floor_coordinates'))

        return Location(
            floor_coordinates = _floor_coordinates,
            installation_id = data.get('installation_id'),
            gateway_id = data.get('gateway_id'),
            floor_id = data.get('floor_id'),
            room_id = data.get('room_id'),
        )
@dataclass
class Status:
    """Class holding the status."""

    on: bool
    locked: bool | None
    manual_override: bool | None
    value: int 

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Status:
        return Status(
            # on = True if status = 1
            on = data.get('status') == 1,
            locked = data.get('locked'),
            value = data.get('dimmer'),
            manual_override = data.get('manual_override')
        )

@dataclass
class Output:
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
    idx: int 
    local_id: int
    name: str
    output_type: str 
    location: Location | None
    capabilities: List | None
    metadata: dict | None
    status: Status | None
    last_state_change: float | None
    version: str | None

    @staticmethod
    def from_dict(data: dict[str, Any]) -> Output | None:
        """Return Output object from OpenMotics API response.
        Args:
            data: The data from the OpenMotics API.
        Returns:
            A Output object.
        """
        output_type = OPENMOTICS_OUTPUT_TYPE_TO_NAME[ data.get('type') ]

        _status: Status = None
        if 'status' in data:
            _status = Status.from_dict(data.get('status'))

        # Switch can always turn on/OFF
        _capabilities = ['ON_OFF']
        # Dimmmer
        if data.get('module_type') == 'D': 
            _capabilities.append("RANGE")

        _location = Location.from_dict(
            {
            'room_id': data.get('room')
            }
        )

        return Output(
            idx = data.get('id'),
            local_id = data.get('id'),
            name = data.get('name'),
            output_type = output_type,
            location = _location,
            capabilities = _capabilities,
            metadata = {},
            status = _status,
            last_state_change = data.get('last_state_change', None),
            version= data.get('version', '1.0'),
        )


    def __str__(self) -> str:
        """Represent the class objects as a string.

        Returns:
            string

        """
        return f"{self.idx}_{self.name}_{self.output_type}"