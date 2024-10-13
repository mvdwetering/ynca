#!/usr/bin/env python3
""" Example of basic YncaApi usage"""

import argparse
import time
import logging

from ynca import YncaApi, Mute, YncaException, Pwr

ZONE_SUBUNITS = ["main", "zone2", "zone3", "zone4"]


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Example application for ynca package."
    )

    parser.add_argument(
        "serial_url",
        help="Can be a devicename like /dev/ttyUSB0 or COM3 for serial or use socket://<ip-or-host>:50000 IP based connections.",
    )
    parser.add_argument(
        "--loglevel",
        choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
        default="INFO",
        help="Define loglevel, default is INFO.",
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)

    print("Create YncaApi instance")
    receiver = YncaApi(args.serial_url)

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
        print(f"- Update SYS {function}, {value}")

    def updated_main(function, value):
        print(f"- Update MAIN {function}, {value}")

    assert receiver.sys is not None
    assert receiver.main is not None
    receiver.sys.register_update_callback(updated_sys)
    receiver.main.register_update_callback(updated_main)

    print("Zones:")
    for zone_attr_name in ZONE_SUBUNITS:
        if zone := getattr(receiver, zone_attr_name):
            print(f"  --- {zone.id} ---")
            print(f"  {zone.zonename=}")
            print(f"  {zone.vol=}")
            print(f"  {zone.inp=}")

    main = receiver.main
    main.pwr = Pwr.ON
    current_volume = main.vol  # Save so it can be restored
    main.vol = -50
    main.vol = -50.5
    main.vol_up(2)
    main.mute = Mute.OFF
    main.mute = Mute.ON
    if current_volume:
        main.vol = current_volume

    print(
        "Wait a bit to see updates coming in as it takes the receiver a while to get it all processed."
    )
    time.sleep(2)

    receiver.close()
