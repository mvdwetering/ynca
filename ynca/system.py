import logging

from typing import Dict

from .connection import YncaConnection, YncaProtocolStatus
from .constants import Subunit
from .function_mixins import PowerFunctionMixin
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class System(PowerFunctionMixin, SubunitBase):
    id = Subunit.SYS

    def __init__(self, connection: YncaConnection):
        """
        Constructor for a Receiver object.
        """
        super().__init__(connection)
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._initialized = False
        self._inp_names: Dict[str, str] = {}

        self._attr_modelname = None
        self._attr_version = None

    def on_initialize(self):
        self._reset_internal_state()

        self._get("MODELNAME")

        # Get user-friendly names for inputs (also allows detection of a number of available inputs)
        # Note that these are not all inputs, just the external ones it seems.
        self._get("INPNAME")

        # Version is also used behind the scenes as a sync for initialization
        # So we should not send it here else it might mess up the synchronization
        # self._get("VERSION")

    def _subunit_message_received_without_handler(
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
    def modelname(self):
        """Get model name"""
        return self._attr_modelname

    @property
    def version(self):
        """Get firmware version"""
        return self._attr_version

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
