"""Init file for the models."""
from pyhaopenmotics.cloud.models.groupaction import GroupAction
from pyhaopenmotics.cloud.models.installation import Installation
from pyhaopenmotics.cloud.models.output import Output
from pyhaopenmotics.cloud.models.shutter import Shutter

# from pyhaopenmotics.cloud.models.thermostat import ThermostatUnit

__all__ = ["Installation", "GroupAction", "Output", "Shutter", ""]
