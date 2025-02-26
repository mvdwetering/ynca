import logging

from ..constants import Subunit
from ..converters import StrConverter
from ..enums import HdmiOutOnOff, Party, PartyMute, Pwr, SpPattern
from ..function import Cmd, EnumFunctionMixin, FunctionMixinBase, StrFunctionMixin
from ..subunit import SubunitBase

logger = logging.getLogger(__name__)

REMOTE_CODE_LENGTH = 8


class System(SubunitBase):
    id = Subunit.SYS

    hdmiout1 = EnumFunctionMixin[HdmiOutOnOff](HdmiOutOnOff)
    hdmiout2 = EnumFunctionMixin[HdmiOutOnOff](HdmiOutOnOff)
    hdmiout3 = EnumFunctionMixin[HdmiOutOnOff](HdmiOutOnOff)
    inpnameaudio1 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameaudio2 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameaudio3 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameaudio4 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameav1 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameav2 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameav3 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameav4 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameav5 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameav6 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameav7 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamedock = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamehdmi1 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamehdmi2 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamehdmi3 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamehdmi4 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamehdmi5 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamehdmi6 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamehdmi7 = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamemultich = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamephono = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnameusb = StrFunctionMixin(Cmd.GET, init="INPNAME")
    inpnamevaux = StrFunctionMixin(Cmd.GET, init="INPNAME")
    modelname = StrFunctionMixin(Cmd.GET)
    party = EnumFunctionMixin[Party](Party)
    partymute = EnumFunctionMixin[PartyMute](PartyMute, Cmd.PUT)
    pwr = EnumFunctionMixin[Pwr](Pwr)
    sppattern = EnumFunctionMixin[SpPattern](SpPattern)

    # No_initialize VERSION to avoid it being sent during initialization
    # It is also used behind the scenes for syncing and would interfere
    version = FunctionMixinBase[str](
        converter=StrConverter(), cmd=Cmd.GET, no_initialize=True
    )

    def partyvol_up(self) -> None:
        """Increase the party volume with one step."""
        self._put("PARTYVOL", "Up")

    def partyvol_down(self) -> None:
        """Decrease the party volume with one step."""
        self._put("PARTYVOL", "Down")

    def remotecode(self, value: str) -> None:
        if len(value) != REMOTE_CODE_LENGTH:
            msg = f"REMOTECODE value must be of length 8, but length of '{value}' is {len(value)}"
            raise ValueError(msg)
        self._put("REMOTECODE", value)
