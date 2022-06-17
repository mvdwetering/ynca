# YNCA

Automation Library for Yamaha receivers that support the YNCA protocol.

Supported receivers according to protocol documentation (not all tested) or logs found on the internet.
There might be more receivers that support this protocol. If you find some let met know so the list can be updated.

> RX-A700, RX-A710, RX-A800, RX-A810, RX-A840, RX-A850, RX-A1000, RX-A1010, RX-A1040, RX-A2000, RX-A2010, RX-A3000, RX-A3010, RX-V671, RX-V867, RX-V871, RX-V1067, RX-V2067, RX-V2600, RX-V3067


## Installation

```bash
python3 -m pip install ynca
```

## Contents

This package contains:

### Ynca class

The Ynca class is exposing the YNCA API as defined in the specification and allows to connect to devices supporting that API.

### Get_all_zone_inputs helper function

This helper gets a list of all the inputs available on the device from the Ynca API to be used with the inputs on the Zone subunits.
It is provided as a convenience because it is a bit tricky to build that list.

### YNCA Terminal

The YNCA Terminal provides an interactive terminal for YNCA commands intended for debugging. Examples on how to start below.

```
python3 -m ynca.terminal /dev/ttyUSB0
python3 -m ynca.terminal socket://192.168.178.21:50000
```

### YNCA Server

Not part of the installed package, but available in the repo there is a very basic YNCA server intended for debugging
 and testing without connecting to a real device. Check the commandline help of `ynca_server.py` for more details.


## Example usage

```python
# Create a Ynca class by specifying the port on your receiver.
# Port could also be e.g. COM3 on Windows or any `serial_url` as supported by PySerial
# Like for example `socket://192.168.1.12:50000` for IP connection
ynca_receiver = Ynca("/dev/tty1")

# Initializing takes a while (multiple seconds) since it communicates
# quite a lot with the actual device to determine its capabilities.
# Later calls to the subunits are fast.
# Note that attributes that are still None after initialization are not supported by the subunits
ynca_receiver.initialize()

# Every subunit has a dedicated attribute on the `Ynca` class.
# The name is the subunit id as used in YNCA.
# The returned subunit class can be used to communicate with the subunit
sys = ynca_receiver.SYS
main = ynca_receiver.MAIN

print(sys.modelname) # Print the modelname of the system
print(main.name) # Print the name of the main zone

# The `get_all_zone_inputs` helper returns a dictionary of available inputs
# with the key being the ID to be used for setting the input on a Zone subunit
# and the value the friendly name (user provided one if available).
# Note that not all inputs might be available to all zones, but
# it is not possible to derive this from the API
for id, name in get_all_zone_inputs(ynca_receiver).items():
    print(f"input {id}: {name}")

# To get notifications when something changes register callback with the subunit
# Note that callbacks are called from a different thread and also should not block for too long.
def update_callback():
    print("Something was updated on the MAIN subunit")

main.register_update_callback(update_callback)

# Examples to control a zone
main.pwr = True
main.mute = Mute.off
main.input = "HDMI3"
main.volume = -50.5
main.volume_up()

# When done call close for proper shutdown
ynca_receiver.close()
```
