#!/usr/bin/env python3
""" A bit of a messy example/manual test script. """

import sys
import time
import logging

from ynca import Ynca, Mute, Subunit, get_all_zone_inputs

ZONE_SUBUNIT_IDS = [Subunit.MAIN, Subunit.ZONE2, Subunit.ZONE3, Subunit.ZONE4]


if __name__ == "__main__":

    logger = logging.getLogger()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)
    logger.setLevel(logging.DEBUG)

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    receiver = Ynca(port)

    print("Initialize start")
    print("This takes a while (approximately 10 seconds on a 2 zone receiver)")
    receiver.initialize()
    print("Initialize done\n")

    def updated_sys():
        print("- Update sys")

    def updated_main():
        print("- Update main")

    receiver.SYS.register_update_callback(updated_sys)
    receiver.MAIN.register_update_callback(updated_main)

    print("Zones:")
    for subunit_id in ZONE_SUBUNIT_IDS:
        if zone := getattr(receiver, subunit_id, None):
            print("  --- {} ---".format(zone.id))
            print(f"  {zone.name=}")
            print(f"  {zone.volume=}")
            print(f"  {zone.input=}")

    print("Inputs:")
    for id, name in get_all_zone_inputs(receiver).items():
        print(f"  {id}: {name}")

    main = receiver.MAIN
    main.pwr = True
    current_volume = main.volume
    main.volume = -50
    main.volume = -50.5
    main.volume_up()
    main.mute = Mute.off
    main.mute = Mute.on
    main.volume = current_volume

    print(
        "Wait a bit to see updates coming in as it takes the receiver a while to get it all processed."
    )
    print("This is more insightful when enabling debug logging.")
    time.sleep(2)

    receiver.close()
