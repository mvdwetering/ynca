import sys
import time
import logging

from ynca import YncaReceiver, Mute, ZONES, Subunit

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
    logging.getLogger("ynca.system").setLevel(logging.DEBUG)
    logging.getLogger("ynca.zone").setLevel(logging.DEBUG)

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    ynca = YncaReceiver(port)
    ynca.initialize()

    sys = ynca.subunits[Subunit.SYS]
    main = ynca.subunits[Subunit.MAIN]
    zone2 = ynca.subunits[Subunit.ZONE2]

    sys.register_update_callback(updated)
    main.register_update_callback(updated_zone1)
    zone2.register_update_callback(updated_zone2)

    print(sys)

    print("Zones:")
    for subunit_id in ZONES:
        try:
            zone = ynca.subunits[subunit_id]
            print("--- {} ---".format(zone.id))
            print(zone)
        except KeyError:
            pass

    print("Inputs:")
    print(ynca.inputs)

    print("Subunits:")
    print(ynca.subunits)

    main.volume = -50
    main.volume = -50.2
    main.volume = -50.4
    main.volume = -50.5
    main.volume = -50.7
    main.volume = -50.8
    main.volume = -51.0
    main.volume = -35

    zone2.on = True
    zone2.mute = Mute.off
    zone2.mute = Mute.on
    zone2.on = False

    remaining = 2
    while remaining >= 0:
        print("Remaining: {}".format(remaining))
        time.sleep(1)
        remaining -= 1

    ynca.close()
