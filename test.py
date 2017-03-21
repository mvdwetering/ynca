import sys
import time
import logging

import ynca

""" Yeah, not really a test, more ofa script to see things are not breaking horribly. """

update_number = 1

if __name__ == "__main__":
    def updated():
        global update_number
        print("Update {}".format(update_number))
        update_number += 1

    logger = logging.getLogger()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    #logging.getLogger("ynca.connection").setLevel(logging.DEBUG)

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    receiver = ynca.YncaReceiver(port, updated)

    print(receiver)

    print("Zones:")
    for zone in receiver.zones:
        print("--- {} ---".format(zone))
        print(receiver.zones[zone])
    print("Inputs:")
    print(receiver.inputs)

    receiver.zones["MAIN"].volume = -50
    receiver.zones["MAIN"].volume = -50.2
    receiver.zones["MAIN"].volume = -50.4
    receiver.zones["MAIN"].volume = -50.5
    receiver.zones["MAIN"].volume = -50.7
    receiver.zones["MAIN"].volume = -50.8
    receiver.zones["MAIN"].volume = -51.0
    receiver.zones["MAIN"].volume = -35

    remaining = 2
    while remaining >= 0:
        print("Remaining: {}".format(remaining))
        time.sleep(1)
        remaining -= 1

