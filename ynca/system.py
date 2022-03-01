import threading
import logging

from typing import Callable, Dict, List, Set

from .connection import YncaConnection, YncaProtocolStatus
from .errors import YncaInitializationFailedException
from .subunit import SubunitBase

logger = logging.getLogger(__name__)


class System(SubunitBase):
    def __init__(self, connection: YncaConnection):
        """
        Constructor for a Receiver object.
        """
        super().__init__("SYS", connection)

        self._initialized_event = threading.Event()
        self._reset_internal_state()

    def _reset_internal_state(self):
        self._initialized = False
        self._power = None
        self._model_name = None
        self._version = None
        self.inputs: Dict[str, str] = {}
        self._initialized_event.clear()

    def initialize(self):
        """
        Initializes the receiver.

        Communicates with the device to determine capabilities.
        This is a long running function!
        It will take several seconds to complete
        """
        logger.info("SYS initialization start.")

        self._reset_internal_state()

        self._get("MODELNAME")
        self._get("PWR")

        # Get user-friendly names for inputs (also allows detection of a number of available inputs)
        # Note that these are not all inputs, just the external ones it seems.
        self._get("INPNAME")

        # Use version as a "sync" command to know when we have all responses
        self._get("VERSION")

        if not self._initialized_event.wait(
            4 * 0.125
        ):  # Each command is ~100ms + margin
            raise YncaInitializationFailedException(
                f"Subunit {self.id} initialization failed"
            )

        logger.info("SYS initialization done.")

        self._initialized = True
        self._call_registered_update_callbacks()

    def __str__(self):
        output = []
        for key in self.__dict__:
            output.append("{key}={value}".format(key=key, value=self.__dict__[key]))

        return "\n".join(output)

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

    def _handle_pwr(self, value: str):
        self._power = value == "On"

    def _handle_modelname(self, value: str):
        self._model_name = value

    def _handle_version(self, value: str):
        self._version = value

        # During initialization this is used to signal
        # that initialization is done
        if not self._initialized:
            self._initialized_event.set()

    @property
    def on(self):
        """Get current on state"""
        return self._power

    @on.setter
    def on(self, value: bool):
        """Turn on/off receiver"""
        self._put("PWR", "On" if value is True else "Standby")

    @property
    def model_name(self):
        """Get model name"""
        return self._model_name

    @property
    def version(self):
        """Get firmware version"""
        return self._version
