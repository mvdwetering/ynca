import logging
from enum import Enum
from typing import Dict

from ..constants import Subunit
from ..converters import StrConverter
from ..subunit import SubunitBase
from ..ynca_function import (
    CommandType,
    YncaFunctionBase,
    YncaFunctionEnum,
    YncaFunctionStr,
)
from .function_mixins import Pwr

logger = logging.getLogger(__name__)


class Party(Enum):
    ON = "On"
    OFF = "Off"


class PartyMute(Enum):
    ON = "On"
    OFF = "Off"


class System(SubunitBase):
    id = Subunit.SYS

    inpnameaudio1 = YncaFunctionStr(
        "INPNAMEAUDIO1",
        command_type=CommandType.GET,
        initialize_function_name="INPNAME",
    )
    inpnameaudio2 = YncaFunctionStr(
        "INPNAMEAUDIO2",
        command_type=CommandType.GET,
        initialize_function_name="INPNAME",
    )
    inpnameaudio3 = YncaFunctionStr(
        "INPNAMEAUDIO3",
        command_type=CommandType.GET,
        initialize_function_name="INPNAME",
    )
    inpnameaudio4 = YncaFunctionStr(
        "INPNAMEAUDIO4",
        command_type=CommandType.GET,
        initialize_function_name="INPNAME",
    )
    inpnameav1 = YncaFunctionStr(
        "INPNAMEAV1", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnameav2 = YncaFunctionStr(
        "INPNAMEAV2", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnameav3 = YncaFunctionStr(
        "INPNAMEAV3", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnameav4 = YncaFunctionStr(
        "INPNAMEAV4", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnameav5 = YncaFunctionStr(
        "INPNAMEAV5", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnameav6 = YncaFunctionStr(
        "INPNAMEAV6", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnameav7 = YncaFunctionStr(
        "INPNAMEAV7", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamedock = YncaFunctionStr(
        "INPNAMEDOCK", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamehdmi1 = YncaFunctionStr(
        "INPNAMEHDMI1", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamehdmi2 = YncaFunctionStr(
        "INPNAMEHDMI2", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamehdmi3 = YncaFunctionStr(
        "INPNAMEHDMI3", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamehdmi4 = YncaFunctionStr(
        "INPNAMEHDMI4", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamehdmi5 = YncaFunctionStr(
        "INPNAMEHDMI5", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamehdmi6 = YncaFunctionStr(
        "INPNAMEHDMI6", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamehdmi7 = YncaFunctionStr(
        "INPNAMEHDMI7", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamemultich = YncaFunctionStr(
        "INPNAMEMULTICH",
        command_type=CommandType.GET,
        initialize_function_name="INPNAME",
    )
    inpnamephono = YncaFunctionStr(
        "INPNAMEPHONO", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnameusb = YncaFunctionStr(
        "INPNAMEUSB", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    inpnamevaux = YncaFunctionStr(
        "INPNAMEVAUX", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )

    inpnamephono = YncaFunctionStr(
        "INPNAMEPHONO", command_type=CommandType.GET, initialize_function_name="INPNAME"
    )
    modelname = YncaFunctionStr("MODELNAME")
    party = YncaFunctionEnum[Party]("PARTY", Party)
    partymute = YncaFunctionEnum[PartyMute](
        "PARTYMUTE", PartyMute, command_type=CommandType.PUT
    )
    pwr = YncaFunctionEnum[Pwr]("PWR", Pwr)

    # No_initialize VERSION to avoid it being sent during initialization
    # It is also used behind the scenes for syncing and would interfere
    version = YncaFunctionBase(
        "VERSION",
        converter=StrConverter(),
        command_type=CommandType.GET,
        no_initialize=True,
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

    def remotecode_send(self, value):
        if len(value) != 8:
            raise ValueError(
                f"REMOTECODE value must be of length 8, but was {len(value)} for {value}"
            )
        self._put("REMOTECODE", value)
