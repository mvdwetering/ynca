#!/usr/bin/env python3
""" Example/manual test script. """

import sys
import time
import logging

from ynca import Ynca, Mute, Subunit, YncaException, get_inputinfo_list, Pwr

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
            print(f"  {zone.zonename=}")
            print(f"  {zone.vol=}")
            print(f"  {zone.inp=}")

    print("Inputs:")
    print("  subunit: inp / name")
    print("  -------------------")
    for inputinfo in get_inputinfo_list(ynca_receiver):
        print(f"  {inputinfo.subunit}: {inputinfo.input} / {inputinfo.name}")

    # Set loglevel to debug so you can see the commands
    # sent because of the statements below
    logger.setLevel(logging.DEBUG)

    main = ynca_receiver.MAIN
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

    ynca_receiver.close()
