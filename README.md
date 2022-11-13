# YNCA

Package to control Yamaha receivers that support the YNCA protocol.

Supported receivers according to info found on the internet (not all tested).
There might be more receivers that support this protocol. If you find some let met know so the list can be updated.

> RX-A700, RX-A710, RX-A720, RX-A800, RX-A810, RX-A820, RX-A840, RX-A850, RX-A1000, RX-A1010, RX-A1020, RX-A1040, RX-A2000, RX-A2010, RX-A2020, RX-A3000, RX-A3010, RX-A3020, RX-V475, RX-V671, RX-V673, RX-V867, RX-V871, RX-V1067, RX-V2067, RX-V3067, TSR-700

Note that there is a restriction that only 1 YNCA connection to a receiver can be made at the time (restriction on the receiver side, not this library).
Usually not a problem as the Yamaha AV Control App uses a different protocol which can be used at the same time, but something to be aware of when testing the library.


## Installation

```bash
python3 -m pip install ynca
```

## Contents

Note that the intended API to use is exposed from the toplevel package.

This package contains

### YncaConnection

The YncaConnection class creates a connection with a YNCA receiver and allows to send/receive YNCA commands. It handles throttling and informs of received values through a callback.
Use this if all that is needed is a basic connection to a receiver.

### YncaApi

The YncaApi class is exposing the YNCA API as Python classes and allows to connect to devices supporting that API.
It keeps a cache of last received values so reading is instant as it does not need to query the receiver.

### YNCA Terminal

The YNCA Terminal provides an interactive terminal for YNCA commands intended for manual debugging. Examples on how to start below.

```
python3 -m ynca.terminal /dev/ttyUSB0
python3 -m ynca.terminal socket://192.168.178.21:50000
```

### YNCA Server

Not part of the installed package, but available in the repo there is a very basic YNCA server intended for debugging
 and testing without connecting to a real device. Check the commandline help of `ynca_server.py` for more details.


## Example usage

```python
# Create a YncaApi class by specifying the port on your receiver.
# Port could also be e.g. COM3 on Windows or any `serial_url` as supported by PySerial
# Like for example `socket://192.168.178.21:50000` for IP connection
receiver = YncaApi("/dev/tty1")

# Initializing takes a while (~10 seconds for a 2 zone receiver) since it communicates
# quite a lot with the actual device to determine its capabilities.
# Later calls to the subunits are fast.
# Note that attributes that are still None after initialization are not supported by the subunits
receiver.initialize()

# Every subunit has a dedicated attribute on the `YncaApi` class.
# The name of the attribute is the subunit id as used in YNCA.
# The returned subunit class can be used to communicate with the subunit
sys = receiver.sys
main = receiver.main

print(sys.modelname) # Print the modelname of the system
print(main.zonename) # Print the name of the main zone

# To get notifications when something changes register callback with the subunit
# Note that callbacks are called from a different thread and should not block.
def update_callback(function, value):
    print(f"{function} changed to {value} on the MAIN subunit")

main.register_update_callback(update_callback)

# Examples to control a zone
main.pwr = Pwr.ON
main.mute = Mute.OFF
main.inp = Input.HDMI3
main.vol = -50.5
main.vol_up()

# When done call close for proper shutdown
receiver.close()
```
