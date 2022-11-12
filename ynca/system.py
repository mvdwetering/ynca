from enum import Enum
import logging

from typing import Dict

from .connection import YncaConnection, YncaProtocolStatus
from .constants import Subunit
from .subunit import (
    CommandType,
    StrConverter,
    SubunitBase,
    YncaFunctionBool,
    YncaFunctionEnum,
    YncaFunctionStr,
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


class PartyVol(Enum):
    UP = "Up"
    DOWN = "Down"


def raise_(ex):
    raise ex


class System(SubunitBase):
    id = Subunit.SYS

    modelname = YncaFunctionStr("MODELNAME")
    party = YncaFunctionEnum[Party]("PARTY", Party)
    partymute = YncaFunctionEnum[PartyMute](
        "PARTYMUTE", PartyMute, command_type=CommandType.PUT
    )
    pwr = YncaFunctionEnum[Pwr]("PWR", Pwr)
    remotecode = YncaFunctionStr(
        "REMOTECODE",
        command_type=CommandType.PUT,
        converter=StrConverter(min_len=8, max_len=8),
    )

    # No_initialize VERSION to avoid it being sent during initialization
    # It is also used behind the scenes for syncing and would interfere
    version = YncaFunctionStr(
        "VERSION", command_type=CommandType.GET, no_initialize=True
    )

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

    def __init__(self, connection: YncaConnection) -> None:
        super().__init__(connection)
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._initialized = False
        self._inp_names: Dict[str, str] = {}

    def on_initialize(self):
        self._reset_internal_state()

        # Get user-friendly names for inputs (also allows detection of a number of available inputs)
        # Note that these are not all inputs, just the external ones it seems.
        self._get("INPNAME")

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

    @property
    def inp_names(self) -> Dict[str, str]:
        """Get input names, dictionary of INP-id,INPNAME"""
        return dict(self._inp_names)
