"""Module containing the base of an output."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

# from pydantic import parse_obj_as

from pyhaopenmotics.helpers import merge_dicts

from pyhaopenmotics.openmoticsgw.models.output import Output

if TYPE_CHECKING:
    from pyhaopenmotics.openmoticscloud import OpenMoticsCloud  # pylint: disable=R0401

class OpenMoticsOutputs:  # noqa: SIM119
    """Object holding information of the OpenMotics outputs.

    All actions related to Outputs or a specific Output.
    """

    def __init__(self, omcloud: OpenMoticsCloud) -> None:
        """Init the installations object.

        Args:
            _omcloud: _omcloud
        """
        self._omcloud = omcloud
        self._output_configs: list = None
    
    @property
    def output_configs(self):
        return self._output_configs

    @output_configs.setter
    def output_configs(self, output_configs: list):
        self._output_configs = output_configs

    async def get_all(  # noqa: A003
        self,
        output_filter: str | None = None,
    ) -> list[Output]:
        """Get a list of all output objects.

        Args:
            output_filter: str

        Returns:
            Dict with all outputs
        """
        if self.output_configs is None:
            goc = await self._omcloud.exec_action('get_output_configurations')
            if goc['success'] is True: 
                self.output_configs = goc['config']
                
        outputs_status = await self._omcloud.exec_action('get_output_status')
        status = outputs_status['status']

        data = merge_dicts(self.output_configs, 'status', status)

        self._outputs = [
            Output.from_dict(device) for device in data
        ]
    
        return self._outputs

    async def get_by_id(
        self,
        output_id: int,
    ) -> Output:
        """Get output by id.

        Args:
            output_id: int

        Returns:
            Returns a output with id
        """
        _output: Output = None
        for output in await self.get_all():
            if output.idx == output_id:
                _output = output

        return _output

    async def toggle(
        self,
        output_id: int,
    ) -> dict[str, Any]:
        """Toggle a specified Output object.

        Args:
            output_id: int

        Returns:
            Returns a output with id
        """
        _output = await self.get_by_id(output_id)
        if _output.status.on == True:
            return await self.turn_off(output_id)
        else:
            return await self.turn_on(output_id)

    async def turn_on(
        self,
        output_id: int,
        value: int | None = 100,
    ) -> dict[str, Any]:
        """Turn on a specified Output object.

        Args:
            output_id: int
            value: <0 - 100>

        Returns:
            Returns a output with id
        """
        if value is not None:
            # value: <0 - 100>
            value = min(value, 100)
            value = max(0, value)

        data = {'id' : output_id, 'is_on' : True}
        if value is not None:
            data['dimmer'] = value
        return await self._omcloud.exec_action('set_output', data=data)

    async def turn_off(
        self,
        output_id: int,
    ) -> dict[str, Any]:
        """Turn off a specified Output object.

        Args:
            installation_id: int
            output_id: int

        Returns:
            Returns a output with id
        """
        data = {'id' : output_id, 'is_on' : False}
        return await self._omcloud.exec_action('set_output', data=data)
