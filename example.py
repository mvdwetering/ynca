#!/usr/bin/env python3
""" Example of basic YncaApi usage"""

import sys
import time
import logging

from ynca import YncaApi, Mute, YncaException, Pwr

ZONE_SUBUNITS = ["main", "zone2", "zone3", "zone4"]


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

    receiver = YncaApi(port)

    print("Initialize start")
    print("This takes a while (about 10 seconds on a 2 zone receiver)")
    try:
        receiver.initialize()
        print("Initialize done\n")
    except YncaException as e:
        print("\n-- Exception during initialization")
        print(f"-- Exception class: {type(e).__name__}")
        print(f"-- Description: {e.__doc__}")
        print(f"-- Details: {e}")
        exit(1)

    def updated_sys(function, value):
        print(f"- Update sys {function}, {value}")

    def updated_main(function, value):
        print(f"- Update main {function}, {value}")

    receiver.sys.register_update_callback(updated_sys)
    receiver.main.register_update_callback(updated_main)

    print("Zones:")
    for zone_attr_name in ZONE_SUBUNITS:
        if zone := getattr(receiver, zone_attr_name):
            print("  --- {} ---".format(zone.id))
            print(f"  {zone.zonename=}")
            print(f"  {zone.vol=}")
            print(f"  {zone.inp=}")

    # Set loglevel to debug so you can see the commands
    # sent because of the statements below
    logger.setLevel(logging.DEBUG)

    main = receiver.main
    main.pwr = Pwr.ON
    current_volume = main.vol  # Save so we can restore it
    main.vol = -50
    main.vol = -50.5
    main.vol_up()
    main.mute = Mute.OFF
    main.mute = Mute.ON
    main.vol = current_volume

    print(
        "Wait a bit to see updates coming in as it takes the receiver a while to get it all processed."
    )
    time.sleep(2)

    receiver.close()
