import sys

import time
import ynca.receiver


if __name__ == "__main__":

    port = "/dev/ttyUSB0"
    if len(sys.argv) > 1:
        port = sys.argv[1]

    receiver = ynca.receiver.YncaReceiver(port)

    remaining = 5
    while remaining >= 0:
        print("Remaining: {}".format(remaining))
        time.sleep(1)
        remaining -= 1

    print(receiver)

    print("Zones:")
    print(receiver.zones)
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
