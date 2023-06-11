import logging

from ..constants import Subunit
from ..converters import StrConverter
from ..function import Cmd, EnumFunction, FunctionBase, StrFunction
from ..enums import HdmiOutOnOff, Party, PartyMute, Pwr
from ..subunit import SubunitBase

logger = logging.getLogger(__name__)


class System(SubunitBase):
    id = Subunit.SYS

    hdmiout1 = EnumFunction[HdmiOutOnOff](HdmiOutOnOff)
    hdmiout2 = EnumFunction[HdmiOutOnOff](HdmiOutOnOff)
    hdmiout3 = EnumFunction[HdmiOutOnOff](HdmiOutOnOff)
    inpnameaudio1 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameaudio2 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameaudio3 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameaudio4 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameav1 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameav2 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameav3 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameav4 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameav5 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameav6 = StrFunction(Cmd.GET, init="INPNAME")
    inpnameav7 = StrFunction(Cmd.GET, init="INPNAME")
    inpnamedock = StrFunction(Cmd.GET, init="INPNAME")
    inpnamehdmi1 = StrFunction(Cmd.GET, init="INPNAME")
    inpnamehdmi2 = StrFunction(Cmd.GET, init="INPNAME")
    inpnamehdmi3 = StrFunction(Cmd.GET, init="INPNAME")
    inpnamehdmi4 = StrFunction(Cmd.GET, init="INPNAME")
    inpnamehdmi5 = StrFunction(Cmd.GET, init="INPNAME")
    inpnamehdmi6 = StrFunction(Cmd.GET, init="INPNAME")
    inpnamehdmi7 = StrFunction(Cmd.GET, init="INPNAME")
    inpnamemultich = StrFunction(Cmd.GET, init="INPNAME")
    inpnamephono = StrFunction(Cmd.GET, init="INPNAME")
    inpnameusb = StrFunction(Cmd.GET, init="INPNAME")
    inpnamevaux = StrFunction(Cmd.GET, init="INPNAME")
    modelname = StrFunction(Cmd.GET)
    party = EnumFunction[Party](Party)
    partymute = EnumFunction[PartyMute](PartyMute, Cmd.PUT)
    pwr = EnumFunction[Pwr](Pwr)

    # No_initialize VERSION to avoid it being sent during initialization
    # It is also used behind the scenes for syncing and would interfere
    version = FunctionBase[str](
        converter=StrConverter(), cmd=Cmd.GET, no_initialize=True
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
