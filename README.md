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

### Classes

#### YncaApi

This is the main class to interact with. The YncaApi class is exposing YNCA subunits and their functions as Python classes/datatypes and allows to connect to devices supporting that API. It keeps a cache which gets updated when values are received from the device so reading attributes is instant as it does not need to query the receiver.

#### YncaConnection

The YncaConnection class creates a basic connection with a YNCA receiver and allows to send/receive YNCA commands. It handles throttling as required by the protocol and informs of received values through a callback. The YncaApi class uses this under the hood.

Use this if all that is needed is a basic connection to a receiver.

#### YncaModelInfo

The YncaModelInfo class is information about features that a specific model supports.
It is technically not really related to the protocol, but since there seems to be no other repository with this info I decided to keep it here.

### Tools

#### YNCA Terminal

The YNCA Terminal provides an interactive terminal for manually sending YNCA commands. It is only intended for manual debugging.
It can be started with commands like below.

```
python3 -m ynca.terminal /dev/ttyUSB0
python3 -m ynca.terminal socket://192.168.178.21:50000
```

#### YNCA Server

This is a very basic YNCA server intended to be just enough for debugging and testing without connecting to a real device.

Note that the server needs to be filled with data from an actual device and it will basically just repeat the same answers as the real device gave (with a few exceptions).
Filling the server can be done by providing it with YNCA logging of a real device, like the ones in the YCNA package repository or a log from your own device e.g. by running `example.py` with loglevel DEBUG (uncomment the line in the example code).

It has some additional commandline options for using different ports, binding to a specific host or testing disconnects

```
python3 -m ynca.server <ynca_repo>/logs/RX-A810.txt
python3 -m ynca.server --host 0.0.0.0 --port 12345 <ynca_repo>/logs/RX-A810.txt
python3 -m ynca.server --help
```


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
main.vol_up(2)

# When done call close for proper shutdown
receiver.close()
```
