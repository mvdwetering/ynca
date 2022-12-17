import logging

from ..constants import Subunit
from ..converters import StrConverter
from ..function import Cmd, EnumFunction, FunctionBase, StrFunction
from ..enums import Party, PartyMute, Pwr
from ..subunit import SubunitBase

logger = logging.getLogger(__name__)


class System(SubunitBase):
    id = Subunit.SYS

    inpnameaudio1 = StrFunction("INPNAMEAUDIO1", Cmd.GET, init="INPNAME")
    inpnameaudio2 = StrFunction("INPNAMEAUDIO2", Cmd.GET, init="INPNAME")
    inpnameaudio3 = StrFunction("INPNAMEAUDIO3", Cmd.GET, init="INPNAME")
    inpnameaudio4 = StrFunction("INPNAMEAUDIO4", Cmd.GET, init="INPNAME")
    inpnameav1 = StrFunction("INPNAMEAV1", Cmd.GET, init="INPNAME")
    inpnameav2 = StrFunction("INPNAMEAV2", Cmd.GET, init="INPNAME")
    inpnameav3 = StrFunction("INPNAMEAV3", Cmd.GET, init="INPNAME")
    inpnameav4 = StrFunction("INPNAMEAV4", Cmd.GET, init="INPNAME")
    inpnameav5 = StrFunction("INPNAMEAV5", Cmd.GET, init="INPNAME")
    inpnameav6 = StrFunction("INPNAMEAV6", Cmd.GET, init="INPNAME")
    inpnameav7 = StrFunction("INPNAMEAV7", Cmd.GET, init="INPNAME")
    inpnamedock = StrFunction("INPNAMEDOCK", Cmd.GET, init="INPNAME")
    inpnamehdmi1 = StrFunction("INPNAMEHDMI1", Cmd.GET, init="INPNAME")
    inpnamehdmi2 = StrFunction("INPNAMEHDMI2", Cmd.GET, init="INPNAME")
    inpnamehdmi3 = StrFunction("INPNAMEHDMI3", Cmd.GET, init="INPNAME")
    inpnamehdmi4 = StrFunction("INPNAMEHDMI4", Cmd.GET, init="INPNAME")
    inpnamehdmi5 = StrFunction("INPNAMEHDMI5", Cmd.GET, init="INPNAME")
    inpnamehdmi6 = StrFunction("INPNAMEHDMI6", Cmd.GET, init="INPNAME")
    inpnamehdmi7 = StrFunction("INPNAMEHDMI7", Cmd.GET, init="INPNAME")
    inpnamemultich = StrFunction("INPNAMEMULTICH", Cmd.GET, init="INPNAME")
    inpnamephono = StrFunction("INPNAMEPHONO", Cmd.GET, init="INPNAME")
    inpnameusb = StrFunction("INPNAMEUSB", Cmd.GET, init="INPNAME")
    inpnamevaux = StrFunction("INPNAMEVAUX", Cmd.GET, init="INPNAME")
    modelname = StrFunction("MODELNAME", Cmd.GET)
    party = EnumFunction[Party]("PARTY", Party)
    partymute = EnumFunction[PartyMute]("PARTYMUTE", PartyMute, Cmd.PUT)
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
