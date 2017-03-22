Design stuff document
=====================

This file contains some design decisions. Mainly for future me.

Scope
=====
The library is intended for automation applications, so control, not configuration.
So things like setting/reading volume, mute inputs are in.
Things like setting name, speaker delays etc... are out for now.

Controlling the subunits like Tuner and other Mediaplayer-like components would be nice, but also out of scope for now.


Input detection
===============
There is no explicit way to check which inputs are supported on the unit or per subunit.


Detection of inputs on the unit
-------------------------------
The availability of a subset of inputs can be deduced in 2 ways:
 * Get the ``INPUTNAMES`` this returns inputs that can be renamed
 * Use the ``AVAIL`` command to check for subunits that are inputs

The first method gives all inputs that can be renamed which seems to be all inputs that have a physical connection.
The second method can be used to detect available subunits (e.g. ``TUN``) and then know that the ``TUNER`` input is
available.

The combination of both should give all inputs.


Detection of the inputs on the zone
-----------------------------------
The seems to be no way to check which inputs are available per zone.

The ``MAIN`` zone seems to have all inputs. Other zones have less. Mainly the video inputs seem missing, but also
some audio.

For now lets not attempt to limit zone inputs.


Zone detection
==============
Since there is no explicit command for supported zones, just check availability by checking all known zone subunits
 (``MAIN``, ``ZONE2``, ``ZONE3`` and ``ZONE4``), if they respond properly to ``AVAIL`` then they are on the device.


Keep alive
==========
The unit can go to sleep of break the connection in case of IP.
The first command received when the unit is asleep is lost.
To avoid this keep the connection alive by sending a dummy command when the connection is idle for a while.
The YNCA spec recommends using the ``@SYS:MODELNAME=?`` command.


Update callback
===============
The current update callback does not indicate what changed.
I currently have no need to know what changed, this can always be implemented later.
A nice way would be to allow subscriptions on attributes, but there seems no standard way to do that.
