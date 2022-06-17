#!/usr/bin/env python3
""" Example/manual test script. """

import sys
import time
import logging

from ynca import (
    Ynca,
    Mute,
    Subunit,
    YncaException,
    get_all_zone_inputs,
)

ZONE_SUBUNIT_IDS = [Subunit.MAIN, Subunit.ZONE2, Subunit.ZONE3, Subunit.ZONE4]


if __name__ == "__main__":

    logger = logging.getLogger()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    )
    logger.addHandler(console_handler)
    # logger.setLevel(logging.DEBUG)

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    ynca_receiver = Ynca(port)

    print("Initialize start")
    print("This takes a while (approximately 10 seconds on a 2 zone receiver)")
    try:
        ynca_receiver.initialize()
        print("Initialize done\n")
    except YncaException as e:
        print("\n-- Exception during initialization")
        print(f"-- Exception class: {type(e).__name__}")
        print(f"-- Description: {e.__doc__}")
        print(f"-- Details: {e}")
        exit(1)

    def updated_sys():
        print("- Update sys")

    def updated_main():
        print("- Update main")

    ynca_receiver.SYS.register_update_callback(updated_sys)
    ynca_receiver.MAIN.register_update_callback(updated_main)

    print("Zones:")
    for subunit_id in ZONE_SUBUNIT_IDS:
        if zone := getattr(ynca_receiver, subunit_id, None):
            print("  --- {} ---".format(zone.id))
            print(f"  {zone.name=}")
            print(f"  {zone.volume=}")
            print(f"  {zone.input=}")

    print("Inputs:")
    for id, name in get_all_zone_inputs(ynca_receiver).items():
        print(f"  {id}: {name}")

    # Set loglevel to debug so you can see the commands
    # sent because of the statements below
    logger.setLevel(logging.DEBUG)

    main = ynca_receiver.MAIN
    main.pwr = True
    current_volume = main.volume  # Save so we can restore it
    main.volume = -50
    main.volume = -50.5
    main.volume_up()
    main.mute = Mute.off
    main.mute = Mute.on
    main.volume = current_volume

    print(
        "Wait a bit to see updates coming in as it takes the receiver a while to get it all processed."
    )
    time.sleep(2)

    ynca_receiver.close()
