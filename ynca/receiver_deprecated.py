import logging
from typing import Callable, Dict

from .get_all_zone_inputs import get_all_zone_inputs
from .ynca import (
    Ynca,
)


class Receiver(Ynca):
    """
    Receiver class has been deprecated and replaced by the Ynca class.
    The Ynca class is basically a renamed Receiver without the "inputs" method which does not exist in the YNCA API.
    The inputs method on the Receiver class has been replaced by the "get_inputinfo_list" helper function.
    """

    def __init__(self, serial_url: str, disconnect_callback: Callable[[], None] = None):
        logging.warning("Receiver class is deprecated. Use Ynca class instead.")
        super().__init__(serial_url, disconnect_callback)

    @property
    def inputs(self) -> Dict[str, str]:
        logging.warning(
            "This method is deprecated. Use 'get_inputinfo_list' helper function instead."
        )

        return get_all_zone_inputs(self)
