import sys

import time
import ynca

import logging

if __name__ == "__main__":

    logger = logging.getLogger()

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(console_handler)
    logger.setLevel(logging.INFO)
    #logging.getLogger("ynca.connection").setLevel(logging.WARN)

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    receiver = ynca.YncaReceiver(port)

    remaining = 5
    while remaining >= 0:
        print("Remaining: {}".format(remaining))
        time.sleep(1)
        remaining -= 1

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
    receiver.zones["MAIN"].volume = -51.11234
