import logging

from typing import Dict

from .connection import YncaConnection, YncaProtocolStatus
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class System(SubunitBase):
    def __init__(self, connection: YncaConnection):
        """
        Constructor for a Receiver object.
        """
        super().__init__("SYS", connection)
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._initialized = False
        self.inputs: Dict[str, str] = {}

        self._attr_pwr = None
        self._attr_modelname = None
        self._attr_version = None

    def on_initialize(self):
        self._reset_internal_state()

        self._get("MODELNAME")
        self._get("PWR")

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
            self.inputs[input_id] = value
        else:
            updated = False

        return updated

    @property
    def on(self):
        """Get current on state"""
        return self._attr_pwr == "On" if self._attr_pwr is not None else None

    @on.setter
    def on(self, value: bool):
        """Turn on/off receiver"""
        self._put("PWR", "On" if value is True else "Standby")

    @property
    def modelname(self):
        """Get model name"""
        return self._attr_modelname

    @property
    def version(self):
        """Get firmware version"""
        return self._attr_version
