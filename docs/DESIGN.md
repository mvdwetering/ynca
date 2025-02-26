# Design stuff document

This file contains some design decisions. Mainly intended for future me.

## Scope

The library was initially intended for automation applications, so focused on control, not configuration.
The scope changed to providing an interface that allows to set/get data using familiar YNCA vocabulary.

Since the amount of supported functions impacts the `initialize`time functions will only be added when someone has a usecase for it and not just all off them.

## API guidelines

Some guidelines I try to follow when adding functions to the API.

* YNCA functions supporting GET are modelled as attributes
  * If the function also supports PUT for the value this attribute will also be writable
* YNCA functions that _only_ support PUT are modelled as methods
  * While it is possible to create write only attributes they felt weird to use.
* YNCA functions that perform actions are modelled as methods
* Attribute names on the API follow naming as used in YNCA but in lowercase; except where not possible due to Python limitations. E.g. "2chdecoder" becomes "twochdecoder"
* Method names on the API follow naming as used on YNCA but in lowercase with the "action" postfixed. E.g. "vol_up()" or "remote_send()"
* While all values on YNCA are transmitted as strings these are converted to Python types
  * Strings stay strings
  * Numbers become integers or floats
  * Multiple options are mapped to Enums
    * Each function will have its own Enum even though values are the same. On multiple occasions it has turned out that possible values have changed between receivers. Having individual Enums allows to just extend the impacted one without impacting other attributes.
    * All enums will have an "UNKNOWN" field for the case where a receiver responds with an unknown value. In these cases, a warning will be logged. This UNKNOWN mapping is to avoid exceptions when mapping to an Enum which would break the code. Unknown values occur because there is no official documentation available and new receivers might support more/different values.
* These are guidelines, exceptions can be made.

Note:
While using attributes to read/write values is pretty neat (and was a nice learning on how to use descriptors) it is a bit weird as you can write a value and it might not have been updated yet when you read it fast enough (sending the command and receiving response takes time). I am not planning to change it any time soon as I do like to just write attributes and not have functions for everything which makes the usage look more messy (IMHO).

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

The `@SYS:MODELNAME=?` command is used for it as it is available on all receivers.

## Future?

Some ideas for future additions or iterations

### Use asyncio

This would make it a better fit for Home Assistant. Might also make communication easier?

There does not seem to be an easy way to wrap the existing API with an asyncio layer in a nice way. So would be an almost complete rewrite?
Would also need a different API as it is not possible to `await` attributes.

Maybe something like:

```python
zone.vol.put(12)  # Send command to receiver
zone.vol.get()    # Would request value at receiver and return value
zone.vol.value()  # Would return last received value from cache
zone.vol.is_supported
```

Try and find integrations with similar challenges and see how they solved it.

### Real GET requests

Somehow I made the assumption there was no real request/response. Just send a command and an update will come from the receiver or not.

However this is only true for PUT requests, it wil only send an update when calues actualy change.
For GET commands there should(==assumption) always be a response. Either the value or an error.

This might also allow for better feature detection. Maybe performing a GET can be used to detect if something is suppported.
Getting a value is easy, but maybe supported commands will still give an @RESTRICTED on the GET even if it is a PUT only command.
Need to check for event only updates if they exist.

That might also explain the lists of GET commands found on the internet to indicate what is supported for a device.

Would allow for an API where attributes are only added when _really_ supported by that specific model and not in general.

### Better events/updates

Currently events/updates from the receiver are just passed in a callback with everything as strings.

A better version would be nice.

* Typed arguments?
* Register for specific updates (next to all?)
* Would still need a raw callback

### Other

Now all zones are the same, which is true for most things, but there are some things like @MAIN:HDMIOUT I have only seen on MAIN and does not seem to make much sense on ZONE2 or others. Maybe it would be good to not have them all the same by default? Could save some initialization time... But on the other hand could result in missing features on a Zone because not encountered yet. Now it just-works.
