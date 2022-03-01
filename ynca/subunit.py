import logging

from typing import Callable, Dict, List, Set

from .connection import YncaConnection, YncaProtocolStatus

logger = logging.getLogger(__name__)


class SubunitBase:
    def __init__(self, id: str, connection: YncaConnection):
        """
        Baseclass for Subunits, should be subclassed do not instantiate manually.
        """
        self.id = id
        self._connection = connection

        self._update_callbacks: Set[Callable[[], None]] = set()
        self._initialized = False

        self._connection.register_message_callback(self._protocol_message_received)

    def initialize(self):
        """
        Initializes the data for the subunit.

        Needs to be implemented in derived classes.
        """
        raise NotImplementedError()

    def _subunit_message_received_without_handler(
        self, status: YncaProtocolStatus, function_: str, value: str
    ) -> bool:
        """
        Called when a message for this subunit was received with no handler
        Implement in subclasses for cases where a simple handler is not enough.
        """
        return False

    def close(self):
        self._connection.unregister_message_callback(self._protocol_message_received)
        self._connection = None
        self._update_callbacks = set()

    def _protocol_message_received(
        self, status: YncaProtocolStatus, subunit: str, function_: str, value: str
    ):
        if status is not YncaProtocolStatus.OK or self.id != subunit:
            # Can't really handle errors since at this point we can't see to what command it belonged
            return

        updated = False
        handler = getattr(self, f"_handle_{function_.lower()}", None)
        if handler is not None:
            handler(value)
            updated = True
        else:
            updated = self._subunit_message_received_without_handler(
                status, function_, value
            )

        if updated:
            self._call_registered_update_callbacks()

    def _put(self, function_: str, value: str):
        self._connection.put(self.id, function_, value)

    def _get(self, function_: str):
        self._connection.get(self.id, function_)

    def register_update_callback(self, callback: Callable[[], None]):
        self._update_callbacks.add(callback)

    def unregister_update_callback(self, callback: Callable[[], None]):
        self._update_callbacks.remove(callback)

    def _call_registered_update_callbacks(self):
        if self._initialized:
            for callback in self._update_callbacks:
                callback()
