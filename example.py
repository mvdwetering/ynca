#!/usr/bin/env python3
""" A bit of a messy example/manual test script. """

import sys
import time
import logging

from ynca import Receiver, Mute, ZONES, Subunit

if __name__ == "__main__":

    def updated():
        print("- Update sys")

    def updated_main():
        print("- Update main")

    def updated_zone2():
        print("- Update zone2")

    logger = logging.getLogger()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)
    # logging.getLogger("ynca.connection").setLevel(logging.DEBUG)
    # logging.getLogger("ynca.receiver").setLevel(logging.DEBUG)
    # logging.getLogger("ynca.subunit").setLevel(logging.DEBUG)
    # logging.getLogger("ynca.system").setLevel(logging.DEBUG)
    # logging.getLogger("ynca.zone").setLevel(logging.DEBUG)

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    receiver = Receiver(port)
    print("Initialize start")
    receiver.initialize()
    print("Initialize done")

    sys = receiver.subunits[Subunit.SYS]
    main = receiver.subunits[Subunit.MAIN]
    zone2 = receiver.subunits[Subunit.ZONE2]

    sys.register_update_callback(updated)
    main.register_update_callback(updated_main)
    zone2.register_update_callback(updated_zone2)

    print(sys)

    print("Zones:")
    for subunit_id in ZONES:
        try:
            zone = receiver.subunits[subunit_id]
            print("--- {} ---".format(zone.id))
            print(f"{zone.name=}")
            print(f"{zone.volume=}")
            print(f"{zone.input=}")
        except KeyError:
            pass

    print("Inputs:")
    print(receiver.inputs)

    print("Subunits:")
    print(receiver.subunits)

    main.on = True
    current_volume = main.volume
    main.volume = -50
    main.volume = -50.5
    main.volume_up()
    main.volume = current_volume

    zone2.on = True
    zone2.mute = Mute.off
    zone2.mute = Mute.on
    zone2.on = False

    print(
        "Wait a bit to see updates coming in as it takes the receiver a while to get it all processed"
    )
    time.sleep(2)

    receiver.close()
