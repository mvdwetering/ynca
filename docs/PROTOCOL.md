# YNCA Protocol recap

This is a short collection of the basics for the YNCA protocol. The real specs are always leading!

Known receivers that support YNCA (there may be more):
RX-V671, RX-A710, RX-V871, RX-A810, RX-A1010, RX-A2010 and RX-A3010


## Description

YNCA is a protocol to control certain Yamaha receivers.
The protocol can be transmitted over serial or IP.

There is another control protocol over IP for Yamaha receivers called YNC.
YNCA is simpler, but more limited.

The YNCA spec refers to setting a value as a `PUT` and reading a value as `GET`.
Both commands have the same format `@SUBUNIT:FUNCTION=VALUE`
For a `GET` the `VALUE` will always be '?'

The receiver will generate messages when a value changes or when a `GET` command is received.
Note there is no way to tell if a message is because of a `GET` request or the value got changes in another way
(e.g. using the remote control or buttons on the device)
This also means that sending a `PUT` not always results in a message, only when the value changes!

The receiver is split up in SUBUNITs, examples are zones (e.g. MAIN), inputs (e.g. TUN for the Tunre) and the system 'SYS'

## Examples

Set input of the main zone to `HDMI1` = `@MAIN:INP=HDMI1`

Get the current volume for `ZONE2` = `@ZONE2:VOL=?` the receiver will respond with:
`@ZONE2:VOL=12.5`

## Errors

There are 2 error types

### @RESTRICTED

This response occurs when a valid YNCA command was sent, but the command is (temporarily) not applicable to the unit
(e.g. setting `VOL` when the unit is in standby or accessing a function not available on the unit)

### @UNDEFINED

This response occurs when an invalid YNCA command is sent

## Weirdnesses

Some notes on weird/unexpected behaviour found when dealing with YNCA devices

### Fixed volume

Zones with fixed volume do _not_ give errors when trying to change the volume. Would have expected @RESTRICTED

### Scene activation not working

For some receivers activating scenes does not work they answer with @RESTRICTED.
See https://github.com/mvdwetering/yamaha_ynca/issues/19 for logs.

Currently known receivers that behave like this: RX-475

### No names

Some receivers respond with @UNDEFINED for ZONENAME and SCENENAME requests.
Strange part is that the user seems to be able to change names on the receiver (or only in the app?), but that info is not available through YNCA.
See https://github.com/mvdwetering/yamaha_ynca/issues/8 for logs

Currently known receivers that behave like this: TSR-700


