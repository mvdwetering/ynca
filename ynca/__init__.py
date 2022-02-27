import logging
from typing import Dict

from .connection import YncaConnection, ynca_console
from .constants import DSP_SOUND_PROGRAMS, Mute
from .receiver import YncaReceiver
from .zone import YncaZone

logging.getLogger(__name__).addHandler(logging.NullHandler())


class Ynca:
    def __init__(
        self,
        connection: YncaConnection,
        receiver: YncaReceiver,
        zones: Dict[str, YncaZone],
    ):
        """This constructor is intended to be called from the factorymethod create_from_serial_url"""
        self._connection = connection
        self.receiver = receiver
        self.zones = zones

    @staticmethod
    def create_from_serial_url(serial_url: str):
        """
        Creates a Ynca instance with an initialized connection, receiver and zones.
        This call takes several seconds.
        """
        connection = YncaConnection(serial_url)
        connection.connect()

        receiver = YncaReceiver(connection)
        receiver.initialize()

        zones: Dict[str, YncaZone] = {}
        for zone_id in receiver.zones:
            zone = YncaZone(zone_id, connection, receiver.inputs)
            zone.initialize()
            zones[zone_id] = zone

        return Ynca(connection, receiver, zones)

    def close(self):
        self.receiver.close()
        for zone in self.zones.values():
            zone.close()
        self._connection.close()
