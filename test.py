import sys
import time
import logging

from ynca import Ynca, Mute

""" Yeah, not really a test, more of a script to see things are not breaking horribly. """

update_number = 1

if __name__ == "__main__":

    def updated():
        global update_number
        print("Update {}".format(update_number))
        update_number += 1

    def updated_zone1():
        print("- Update zone1")

    def updated_zone2():
        print("- Update zone2")

    logger = logging.getLogger()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    logging.getLogger("ynca.connection").setLevel(logging.DEBUG)
    logging.getLogger("ynca.receiver").setLevel(logging.DEBUG)
    logging.getLogger("ynca.zone").setLevel(logging.DEBUG)

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    ynca = Ynca.create_from_serial_url(port)

    ynca.receiver.register_update_callback(updated)
    ynca.zones["MAIN"].register_update_callback(updated_zone1)
    ynca.zones["ZONE2"].register_update_callback(updated_zone2)

    print(ynca.receiver)

    print("Zones:")
    for id, zone in ynca.zones.items():
        print("--- {} ---".format(id))
        print(zone)

    print("Inputs:")
    print(ynca.receiver.inputs)

    ynca.zones["MAIN"].volume = -50
    ynca.zones["MAIN"].volume = -50.2
    ynca.zones["MAIN"].volume = -50.4
    ynca.zones["MAIN"].volume = -50.5
    ynca.zones["MAIN"].volume = -50.7
    ynca.zones["MAIN"].volume = -50.8
    ynca.zones["MAIN"].volume = -51.0
    ynca.zones["MAIN"].volume = -35

    ynca.zones["ZONE2"].on = True
    ynca.zones["ZONE2"].mute = Mute.off
    ynca.zones["ZONE2"].mute = Mute.on
    ynca.zones["ZONE2"].on = False

    remaining = 2
    while remaining >= 0:
        print("Remaining: {}".format(remaining))
        time.sleep(1)
        remaining -= 1

    ynca.close()
