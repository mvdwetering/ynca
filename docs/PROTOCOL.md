# YNCA Protocol recap

This is a short collection of the basics for the YNCA protocol.
The final source of thruth is how the devices actually respond!

Known receivers that support YNCA (there may be more):
RX-V671, RX-A710, RX-V871, RX-A810, RX-A1010, RX-A2010 and RX-A3010


## Description

YNCA is a protocol to control certain Yamaha receivers.
The protocol can be transmitted over serial or a TCP/IP socket.

Serial connection parameters: 9600,8,N,1
TCP port: 50000 (standard, can be customized by user)

There are other protocols for Yamaha receviers like YNC and Musiccast.
YNCA is simpler, but more limited.

In YNCA setting a value is referred to as a `PUT` and reading a value as `GET`.
Both commands have the same format `@SUBUNIT:FUNCTION=VALUE`
For a `GET` the `VALUE` will always be '?'

The receiver will generate messages when a value changes, when a `GET` command is received or other releted events (e.g. turning on a zone will send multiple messages).
Note there is no way to tell if a message is because of a `GET` request or the value got changed in another way (e.g. using the remote control or buttons on the device)
This also means that sending a `PUT` will not always results in a message as messages are usually (not always) only sent when the value changes.

The receiver is split up in SUBUNITs, examples are zones (e.g. MAIN, ZONE2), inputs (e.g. TUN for the Tuner) and the system 'SYS'

## Examples

To set input of subunit MAIN to `HDMI1` use command `@MAIN:INP=HDMI1`

To get the current volume for subunit `ZONE2` use command `@ZONE2:VOL=?` and the receiver will respond with: `@ZONE2:VOL=12.5` (value obviously depends on current value)

## Errors

There are 2 error types.

Note that there seems to be no error response when writing to a GET only function (e.g. setting MODELNAME). In that case there is no response at all.

### @RESTRICTED

This response occurs when a valid YNCA command was sent, but the command is (temporarily) not applicable to the unit
(e.g. setting `VOL` when the unit is in standby or accessing a function not available on the unit like a Zone that does not exist)

### @UNDEFINED

This response occurs when an invalid/unknown YNCA command is sent
