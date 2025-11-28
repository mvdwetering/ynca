# YNCA

Package to control Yamaha receivers that support the YNCA protocol.

>Note that only 1 YNCA connection to a receiver can be made at the time. This is a restriction on the receiver side, not this library.
>It is usually not a problem since the Yamaha AV Control App uses a different protocol which can be used at the same time, but something to be aware of when testing the library.

## Working models

Unfortunately, Yamaha does not mention in the manuals if a model supports the YNCA protocol that this library uses.

The table of working models below is based on reports from users and info found on the internet. Model years were mostly taken from this [Yamaha AVR model history page](https://kane.site44.com/Yamaha/Yamaha_AVR_model_history.html).

Based on this information, receivers in the mentioned series from 2010 onwards are likely to work. So even if your model is not listed, just give it a try.

If your receiver works and is not in the list, please post a message in the [discussions](https://github.com/mvdwetering/yamaha_ynca/discussions) so it can be added.

| Year | Series | Models |
| --- | --- | --- |
| 2010 | AVENTAGE | RX-A700, RX-A800, RX-A1000, RX-A2000, RX-A3000 |
|| RX-V | RX-V867, RX-V1067, RX-V2067, RX-V3067 |
|| HTR | HTR-8063 |
| 2011 | AVENTAGE | RX-A710, RX-A810, RX-A1010, RX-A2010, RX-A3010 |
|| RX-V | RX-V671, RX-V771, RX-V871, RX-V1071, RX-V2071, RX-V3071 |
|| HTR | HTR-6064 |
| 2012 | AVENTAGE | RX-A720, RX-A820, RX-A1020, RX-A2020, RX-A3020 |
|| RX-V | RX-V473, RX-V573, RX-V673, RX-V773 |
|| HTR | HTR-4065, HTR-7065 |
| 2013 | AVENTAGE | RX-A730, RX-A830, RX-A1030, RX-A2030, RX-A3030 |
|| RX-V | RX-V475, RX-V575, RX-V675, RX-V775, RX-V1075, RX-V2075, RX-V3075 |
|| HTR | HTR-4066 |
|| Other | CX-A5000, R-N500, RX-V500D, RX-S600D |
| 2014 | AVENTAGE | RX-A740, RX-A840, RX-A1040, RX-A2040, RX-A3040 |
|| RX-V | RX-V477, RX-V677, RX-V777, RX-V1077, RX-V2077, RX-V3077 |
| 2015 | AVENTAGE | RX-AS710D, RX-A750, RX-A850, RX-A2050, RX-A3050 |
|| RX-V | RX-V679 |
|| Other | CX-A5100, RX-S601D |
| 2016 | AVENTAGE | RX-A660 |
|| RX-V | RX-V481D, RX-V581, RX-V681 |
|| TSR | TSR-7810 |
|| Other | WXC-50 |
| 2017 | AVENTAGE | RX-A870, RX-A2070, RX-A3070 |
|| RX-V | RX-V483, RX-V683 |
|| HTR | HTR-4071 |
| 2018 | AVENTAGE | RX-A880, RX-A3080 |
|| RX-V | RX-V585, RX-V685, RX-V1085 |
|| HTR | HTR-4072 |
|| TSR | TSR-7850 |
|| Other | CX-A5200 |
| 2020 | AVENTAGE | RX-A2A, RX-A4A, RX-A6A |
|| RX-V | RX-V4A, RX-V6A |
|| TSR | TSR-700 |

## Installation

```bash
python3 -m pip install ynca
```

## Contents

The intended API to use is exposed from the toplevel package.

### Classes

#### YncaApi

This is the main class to interact with. The YncaApi class is exposing YNCA subunits and their functions as Python classes/datatypes and allows to connect to devices supporting that API. It keeps a cache which gets updated when values are received from the device so reading attributes is instant as it does not need to query the receiver.

#### YncaConnection

The YncaConnection class creates a basic connection with a YNCA receiver and allows to send/receive YNCA commands. It handles throttling as required by the protocol and informs of received values through a callback. The YncaApi class uses this under the hood.

Use this if all that is needed is a basic connection to a receiver.

#### YncaModelInfo

The YncaModelInfo class is information about features that a specific model supports.
It is technically not really related to the protocol, but since there seems to be no other repository with this info I decided to keep it here.

## Example usage

```python
# Create a YncaApi class by specifying the port on your receiver.
# Port could also be e.g. COM3 on Windows or any `serial_url` as supported by PySerial
# Like for example `socket://192.168.178.21:50000` for IP connection
receiver = YncaApi("/dev/tty1")

# Initializing takes a while (~10 seconds for a 2 zone receiver) since it communicates
# quite a lot with the actual device to determine its capabilities.
# Later calls to the subunits are fast.
# The attributes that are still None after initialization are not supported by the subunits
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

### Tools

The package comes with some tools to help with debugging.

#### YNCA Terminal

The YNCA Terminal provides an interactive terminal for manually sending YNCA commands. It is only intended for manual debugging.
It can be started with commands like below.

```bash
python3 -m ynca.terminal /dev/ttyUSB0
python3 -m ynca.terminal socket://192.168.178.21:50000
```

#### YNCA debug server

This is a very basic YNCA server intended to be just enough for debugging and testing without connecting to a real device.

The server needs to be filled with data from an actual device and it will basically just repeat the same answers as the real device gave (with a few exceptions).
Filling the server can be done by providing it with YNCA logging of a real device, like the ones in the YCNA package repository or a log from your own device e.g. by running `example.py` with loglevel DEBUG (uncomment the line in the example code).

It has some additional commandline options for using different ports, binding to a specific host or testing disconnects

```bash
python3 -m ynca.debug_server <ynca_repo>/logs/RX-A810.txt
python3 -m ynca.debug_server --host localhost --port 12345 <ynca_repo>/logs/RX-A810.txt
python3 -m ynca.debug_server --help
```
