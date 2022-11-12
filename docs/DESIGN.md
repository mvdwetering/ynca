# Design stuff document

This file contains some design decisions. Mainly intended for future me.

## Scope

The library was initially intended for automation applications, so focused on control, not configuration.
The scope changed to providing an interface that allows to set/get data using familiar YNCA vocabulary.

However, since the amount of supported functions impacts the `initialize`time functions will only be added when
someone has a usecase for it and not just all off them.


## API guidelines

Some guidelines I try to follow when adding functions to the API.

* YNCA functions supporting GET are modelled as attributes
    * If the function also support PUT of the value the attribute will be writable
* YNCA functions that perform actions or _only_ support PUT are modelled as methods
    * While it is possible to create write only attributes they felt weird to use. MIght change my mind on it one day...
* Attribute names on the API follow naming (but in lowercase) as used in YNCA except where not possible due to Python limitations. E.g. "2chdecoder" becomes "twochdecoder"
* Method names on the API follow naming (but in lowercase) as used on YNCA with the "action" postfixed. E.g. "vol_up()" or "remote_send()"
* While all values on YNCA are transmitted as strings these are converted to Python types
    * Strings stay strings
    * Numbers become integers or floats
    * Multiple options are mapped to Enums
    * These are guidelines, exceptions can be made.


## Input detection

There is no explicit way to check which inputs are supported on the unit or per subunit.
However it can be derived with some logic.


### Detection of inputs on the unit

The availability of a subset of inputs can be deduced in 2 ways:
 * Get the `INPUTNAMES` this returns inputs that can be renamed
 * Use the `AVAIL` command to check for subunits that are inputs

The first method gives all inputs that can be renamed which seems to be all inputs that have a physical connection.
The second method can be used to detect available subunits (e.g. `TUN`) and then know that the `TUNER` input is available.

The combination of both should give all inputs.


### Detection of the inputs on the zone

The seems to be no way to check which inputs are available per zone.

The `MAIN` zone seems to have all inputs. Other zones have less. Mainly the video inputs seem missing, but also some audio it seems.

For now lets not attempt to detect the exact supported inputs on a zone.


## Zone detection

Since there is no explicit command for supported zones, just check availability by checking all known zone subunits (`MAIN`, `ZONE2`, `ZONE3` and `ZONE4`), if they respond properly to `AVAIL` then they are on the device.


## Keep alive

The unit can go to sleep or break the connection in case of IP.
The first command sent to the unit when it is asleep is lost.
To avoid this keep the connection alive by sending a dummy command when the connection is idle for a while.

The YNCA spec recommends using the `@SYS:MODELNAME=?` command.

