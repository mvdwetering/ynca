# Practicalities

This document describes some notes on weirdness/unexpected behaviour and other practicalities found when working with devices using the YNCA protocol.


## Fixed volume

There seem to be 2 situations where zones have a fixed volume.

 * No volume control at all. This is clearly indicated by the absence of a VOL function, e.g Zone 4 on RX-A6A
 * No volume control related to some specific configuration/setup.

For the second case the zone still reports the VOL function which can be read and does _not_ give errors when trying to change the volume (I would have expected @RESTRICTED).
There are no response/updates on trying to change the volume (as it is fixed). It is unknown which setting causes the volume to become fixed.

For reference, the AV Control Android app also shows volume controls for zone2 which do not work.
The webinterface on the receiver however shows the text "FIXED" for the volume on Zone2
This is based on observations on RX-A810 firmware 1.80/2.01.

Tried to derive from MAXVOL availability, but not available on all non-fixed zones, e.g. RX-V475 1.34/2.06

It is most likely related to the speakerconfiguration indicated by the `@SYS:SPPATTERN1AMP` command which can have values like `Basic`, `7ch +1ZONE`, `5ch BI-AMP` and many more.
My guess would be that when `+1ZONE` is there that means that actual speakers for Zone2 are connected and on the `Basic` case you are supposed to use the preout connections for Zone2.

This needs some more research/data to make a solid conclusion

## Scene activation not working

For some receivers activating scenes does not work and they answer with @RESTRICTED.
See https://github.com/mvdwetering/yamaha_ynca/issues/19 for logs.

Currently known receivers that behave like this:
- RX-V475 1.34/2.06

## No Zone and Scene names

Some receivers respond with @UNDEFINED for ZONENAME and SCENENAME requests.
Strange part is that the user seems to be able to change names on the receiver (or only in the app?), but that info is not available through YNCA.
See https://github.com/mvdwetering/yamaha_ynca/issues/8 for logs

Currently known receivers that behave like this:
- TSR-700 1.53/3.12
- RX-A6A 1.80/3.12

## INITVOLLVL variations

Some receivers report "Off" as value for INITVOLLVL while others (most?) have a specific INITVOLLVLMODE to turn it on/off.
Presumaby receivers that report "Off" have the INITVOLLVL and INITVOLLVLMODE combined.

So assumed functionality is:

* "Off" = Disabled (a.k.a. last state)
* "Mute" = Enabled with Mute
* <number> = Enabled with specific level

Currently known receivers that can report "Off":
- RX-V477 1.28/1.4

## 2CHDECODER

It looks like the 2CHDECODER values completely changed on newer models of receivers.
The older models have support for Dolby Prologic and DTS:Neo settings, while newer models seem to have diffent values.

Values seen until now:
* "AURO-3D"  # Seen on RX-A6A
* "DTS Neural:X"  # Seen on RX-A1060

From a quick look at the product manuals those models do not support the older surround decoder values. AURO-3D does not seem to be available on RX-1060 and it is unknown how to detect AURO-3D support.

