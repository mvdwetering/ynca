from enum import Enum
import logging

from typing import Dict

from .connection import YncaConnection, YncaProtocolStatus
from .constants import Subunit
from .subunit import (
    CommandType,
    SubunitBase,
    YncaFunction,
    YncaFunctionReadOnly,
    YncaFunctionWriteOnly,
)

logger = logging.getLogger(__name__)


class Pwr(Enum):
    ON = "On"
    STANDBY = "Standby"


class Party(Enum):
    ON = "On"
    OFF = "Off"


class PartyMute(Enum):
    ON = "On"
    OFF = "Off"


class System(SubunitBase):
    id = Subunit.SYS

    def __init__(self, connection: YncaConnection) -> None:
        super().__init__(connection)
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._initialized = False
        self._inp_names: Dict[str, str] = {}
        self._attr_version = None

    def on_initialize(self):
        self._reset_internal_state()

        # Get user-friendly names for inputs (also allows detection of a number of available inputs)
        # Note that these are not all inputs, just the external ones it seems.
        self._get("INPNAME")

        # Version is also used behind the scenes as a sync for initialization
        # So we should not send it here else it might mess up the synchronization
        # self._get("VERSION")

    def on_message_received_without_handler(
        self, status: YncaProtocolStatus, function_: str, value: str
    ) -> bool:
        updated = True

        if function_.startswith("INPNAME"):
            input_id = function_[7:]
            if input_id == "VAUX":
                # Input ID used to set/get INP is actually V-AUX so compensate for that mismatch on the API
                input_id = "V-AUX"
            self._inp_names[input_id] = value
        else:
            updated = False

        return updated

    modelname = YncaFunction[str]("MODELNAME", str)
    party = YncaFunction[Party]("PARTY", Party)
    partymute = YncaFunctionWriteOnly[PartyMute]("PARTYMUTE", PartyMute)
    pwr = YncaFunction[Pwr]("PWR", Pwr)

    # No initialize VERSION to avoid it being sent during initialization
    # because it is also used behind the scenes for syncing
    version = YncaFunctionReadOnly[str]("VERSION", str, no_initialize=True)

    @property
    def inp_names(self) -> Dict[str, str]:
        """Get input names, dictionary of INP-id,INPNAME"""
        return dict(self._inp_names)

    @property
    def inputs(self) -> Dict[str, str]:
        logger.warning(
            "The 'inputs' attribute is deprecated and replaced with 'inp_names' to better match naming of the YNCA spec"
        )
        return self.inp_names

    def partyvol_up(self):
        """
        Increase the party volume with one step.
        """
        self._put("PARTYVOL", "Up")

    def partyvol_down(self):
        """
        Decrease the party volume with one step.
        """
        self._put("PARTYVOL", "Down")

    def send_remotecode(self, code: str):
        """Send remote code. These codes are 8 characters long."""
        self._put("REMOTECODE", code)
