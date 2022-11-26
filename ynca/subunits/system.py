import logging

from ..constants import Party, PartyMute, Subunit, Pwr
from ..converters import StrConverter
from ..subunit import SubunitBase
from ..function import (
    Cmd,
    FunctionBase,
    EnumFunction,
    StrFunction,
)

logger = logging.getLogger(__name__)


class System(SubunitBase):
    id = Subunit.SYS

    inpnameaudio1 = StrFunction("INPNAMEAUDIO1", cmd=Cmd.GET, init="INPNAME")
    inpnameaudio2 = StrFunction("INPNAMEAUDIO2", cmd=Cmd.GET, init="INPNAME")
    inpnameaudio3 = StrFunction("INPNAMEAUDIO3", cmd=Cmd.GET, init="INPNAME")
    inpnameaudio4 = StrFunction("INPNAMEAUDIO4", cmd=Cmd.GET, init="INPNAME")
    inpnameav1 = StrFunction("INPNAMEAV1", cmd=Cmd.GET, init="INPNAME")
    inpnameav2 = StrFunction("INPNAMEAV2", cmd=Cmd.GET, init="INPNAME")
    inpnameav3 = StrFunction("INPNAMEAV3", cmd=Cmd.GET, init="INPNAME")
    inpnameav4 = StrFunction("INPNAMEAV4", cmd=Cmd.GET, init="INPNAME")
    inpnameav5 = StrFunction("INPNAMEAV5", cmd=Cmd.GET, init="INPNAME")
    inpnameav6 = StrFunction("INPNAMEAV6", cmd=Cmd.GET, init="INPNAME")
    inpnameav7 = StrFunction("INPNAMEAV7", cmd=Cmd.GET, init="INPNAME")
    inpnamedock = StrFunction("INPNAMEDOCK", cmd=Cmd.GET, init="INPNAME")
    inpnamehdmi1 = StrFunction("INPNAMEHDMI1", cmd=Cmd.GET, init="INPNAME")
    inpnamehdmi2 = StrFunction("INPNAMEHDMI2", cmd=Cmd.GET, init="INPNAME")
    inpnamehdmi3 = StrFunction("INPNAMEHDMI3", cmd=Cmd.GET, init="INPNAME")
    inpnamehdmi4 = StrFunction("INPNAMEHDMI4", cmd=Cmd.GET, init="INPNAME")
    inpnamehdmi5 = StrFunction("INPNAMEHDMI5", cmd=Cmd.GET, init="INPNAME")
    inpnamehdmi6 = StrFunction("INPNAMEHDMI6", cmd=Cmd.GET, init="INPNAME")
    inpnamehdmi7 = StrFunction("INPNAMEHDMI7", cmd=Cmd.GET, init="INPNAME")
    inpnamemultich = StrFunction("INPNAMEMULTICH", cmd=Cmd.GET, init="INPNAME")
    inpnamephono = StrFunction("INPNAMEPHONO", cmd=Cmd.GET, init="INPNAME")
    inpnameusb = StrFunction("INPNAMEUSB", cmd=Cmd.GET, init="INPNAME")
    inpnamevaux = StrFunction("INPNAMEVAUX", cmd=Cmd.GET, init="INPNAME")
    modelname = StrFunction("MODELNAME")
    party = EnumFunction[Party]("PARTY", Party)
    partymute = EnumFunction[PartyMute]("PARTYMUTE", PartyMute, cmd=Cmd.PUT)
    pwr = EnumFunction[Pwr]("PWR", Pwr)

    # No_initialize VERSION to avoid it being sent during initialization
    # It is also used behind the scenes for syncing and would interfere
    version = FunctionBase[str](
        "VERSION", converter=StrConverter(), cmd=Cmd.GET, no_initialize=True
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

    def remotecode(self, value):
        if len(value) != 8:
            raise ValueError(
                f"REMOTECODE value must be of length 8, but length of '{value}' is {len(value)}"
            )
        self._put("REMOTECODE", value)
