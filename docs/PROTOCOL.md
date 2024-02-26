# YNCA Protocol recap

This is a short intro to the basics for the YNCA protocol.
The final source of thruth is how the devices actually respond!

Known receivers that support YNCA (there may be more):
> HTR-4065, HTR-4071, HTR-6064, RX-A660, RX-A700, RX-A710, RX-A720, RX-A740, RX-A750, RX-A800, RX-A810, RX-A820, RX-A830, RX-A840, RX-A850, RX-A1000, RX-A1010, RX-A1020, RX-A1030, RX-A1040, RX-A2000, RX-A2010, RX-A2020, RX-A2070, RX-A3000, RX-A3010, RX-A3020, RX-A3030, RX-A3070, RX-S600D, RX-V473, RX-V475, RX-V477, RX-V481D, RX-V483, RX-V575, RX-V671, RX-V673, RX-V675, RX-V677, RX-V679, RX-V771, RX-V773, RX-V775, RX-V777, RX-V867, RX-V871, RX-V1067, RX-V1071, RX-V1085, RX-V2067, RX-V2071, RX-V3067, RX-V3071, TSR-700, TSR-7850

## Description

YNCA is a protocol to control Yamaha receivers.
The protocol can be transmitted over serial or a TCP/IP socket.

Serial connection parameters: 9600,8,N,1
TCP port: 50000 (standard, can be customized by user)

There are other protocols for Yamaha receivers like YNC and Musiccast.
YNCA is the simpler one it seems, but more limited.

In YNCA setting a value is referred to as a `PUT` and reading a value as `GET`.
Both have the same format `@SUBUNIT:FUNCTION=VALUE`
For a `GET` the `VALUE` will always be '?'

The receiver will generate messages when a value changes, when a `GET` command is received or other related events (e.g. turning on a zone will send multiple messages).
There is no way to tell if a message is because of a `GET` request or the value got changed in another way (e.g. using the remote control or buttons on the device)
This also means that sending a `PUT` will not always result in a message as messages are usually (not always) only sent when the value changes.

The receiver is split up in SUBUNITs, examples are zones (e.g. MAIN, ZONE2), inputs (e.g. TUN for the Tuner) and the system SYS

An easy way to learn about the commands is to connect to the receiver, change some values and observe the value updates coming out.

## Examples

To set input of subunit MAIN to `HDMI1` use command `@MAIN:INP=HDMI1`

To get the current volume for subunit `ZONE2` use command `@ZONE2:VOL=?` and the receiver will respond with: `@ZONE2:VOL=12.5` (value obviously depends on current value)

## Errors

There are 2 error types.

Note that there seems to be no error response when writing to a readonly function (e.g. setting MODELNAME). In that case there is no response at all.

### @RESTRICTED

This response occurs when a valid YNCA command was sent, but the command is (temporarily) not applicable to the unit.
For example setting `VOL` when the unit is in standby or accessing a function not available on the unit like a Zone that does not exist.

### @UNDEFINED

This response occurs when an invalid/unknown YNCA command is sent
