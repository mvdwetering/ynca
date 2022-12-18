# Practicalities

This document describes some notes on weirdness/unexpected behaviour and other practicalities found when working with devices using the YNCA protocol.


## Fixed volume

Zones with fixed volume have a readable volume (so GET works) and do _not_ give errors when trying to change the volume. Would have expected @RESTRICTED.
There are no response/updates on trying to change the volume (as it is fixed)

Tried to derive from MAXVOL availability, but not available on all non-fixed zones, e.g. RX-V475

There seems to be no way to detect fixed volume zones.


## Scene activation not working

For some receivers activating scenes does not work and they answer with @RESTRICTED.
See https://github.com/mvdwetering/yamaha_ynca/issues/19 for logs.

Currently known receivers that behave like this:
- RX-475 1.34/2.06

## No Zone and Scene names

Some receivers respond with @UNDEFINED for ZONENAME and SCENENAME requests.
Strange part is that the user seems to be able to change names on the receiver (or only in the app?), but that info is not available through YNCA.
See https://github.com/mvdwetering/yamaha_ynca/issues/8 for logs

Currently known receivers that behave like this:
- TSR-700 1.53/3.12


