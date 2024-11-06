# Practicalities

This document describes some notes on weirdness/unexpected behaviour and other practicalities found when working with devices using the YNCA protocol.


## Fixed volume

There seem to be 2 situations where zones have a fixed volume.

 * No volume control at all. This is clearly indicated by the absence of a VOL function, e.g Zone 4 on RX-A6A
 * No volume control related to some specific configuration/setup.

For the second case the zone still reports the VOL function which can be read and does _not_ give errors when trying to change the volume (I would have expected @RESTRICTED).
There are no response/updates on trying to change the volume (as it is fixed). It is unknown which setting causes the volume to become fixed.

For reference, the AV Control Android app also shows volume controls for Zone2 which do not work.
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
- RX-V475 1.34/2.06 (probably also RX-V575/HTR-4066/HTR-5066 as they share the same firmware

As a workaround the remote codes for SCENE1 etc... can be sent. This works at least on RX-V475 based on user feedback.

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
* number = Enabled with specific level

Currently known receivers that can report "Off":
- RX-V477 1.28/1.4

## 2CHDECODER

It looks like the 2CHDECODER values completely changed on newer models of receivers.
The older models have support for Dolby Prologic and DTS:Neo settings, while newer models seem to have diffent values.

Values seen until now:
* "AURO-3D" Seen on RX-A6A
* "DTS Neural:X" Seen on RX-A1060 and RX-A3070

From a quick look at the product manuals those models do not support the older surround decoder values. 
However the RX-A3070 does... it supports the DTS:NEO presets and Auto, Dolby Surround, Neural X.

AURO-3D does not seem to be available on RX-1060 and it is unknown how to detect AURO-3D support.

It is unfortunately unknown if it is possible to derive the 2CHDECODER options from other settings.

## SONG vs TRACK for songtitles

It seems that most sources that support METAINFO for songs use SONG for songtitle.

However Spotify uses TRACK instead.

Pandora seems to use TRACK or SONG. Might depend on firmware version?

TRACK is seen in the RX-A6A (1.80/3.12) and TSR-700 (1.53/3.12) logs and on internet mentioned for RX-A850
SONG only seen on internet without mention of receiver or firmware version

## HDMIOUT control

There seem to be 2 methods of controlling HDMIOUT status

### MAIN:HDMIOUT 

This seems to be how older receivers work like RX-A810 or RX-V671

MAIN:HDMIOUT is an enum which can have values depending on the amount of HDMI outputs.

RX-V671 has 1 HDMI output and supports values Off and OUT
RX-A810 has 2 HDMI outputs and supports values Off, OUT1, OUT2 and OUT1 + 2. 

I have only seen it for the MAIN zone, but in theory it might also apply to others?


### SYS:HDMIOUT#

This seems to be for newer receivers like TSR-700 and RX-A6A

SYS:HDMIOUT# is a boolean that can have values On and Off. This command toggles a specific HDMIOUT on/off.

This command has been seen for HDMIOUT 1, 2 and 3.

What makes this command a bit weird is while it is part of the SYS subunit it can _only_ be controlled when the related zone is On. So for example you can only control HDMIOUT1 when the MAIN zone is On. See logging in [this discussion comment ](https://github.com/mvdwetering/yamaha_ynca/discussions/119#discussioncomment-6103924)

That seems workable for HDMIOUT 1 and 2 since those always seem to be related to the MAIN zone, but HDMIOUT3 is special and can be linked with ZONE2 and ZONE4 on an RX-A4A or RX-A6A according to the manual. It is unknown if/how it is possible to figure out to which zone it is configured. Would need logging when changing that setting.

In RX-A6A logging (see logs directory) it seems like both zones (2 and 4) report HDMIOUT3 as a result of requesting BASIC.

## AUDIO input

Some receivers have a single audio input and that input is called AUDIO. Receivers with multiple audio inputs have them called AUDIO1, AUDIO2 etc...

Seen on RX-V475 receiver in [issue #230](https://github.com/mvdwetering/yamaha_ynca/issues/230), but probably also applies to RX-V575/HTR-4066/HTR-5066 as they share the same firmware.

For some reason this input is _not_ reported when requesting the input names with `@SYS:INPNAME=?` (unlike AUDIO1, AUDIO2 inputs). This makes it impossible to automatically detect if the input is supported by the receiver. The receiver does respond with `@RESTRICTED` when requesting `@SYS:INPNAMEAUDIO1=?` or `@SYS:TRIG1INPAUDIO1=?` instead of `@UNDEFINED`. However these responses are currently not really handled by the library. ~~Building support for that will be hard as there is not a guarenteed request/response mechanism due to the asynchronous nature of the protocol~~ (not true, a GET will result in a response or error).

## Zone A/B receivers

(this section is compiled from findings in https://github.com/mvdwetering/yamaha_ynca/issues/320)

There are receivers that have zones indicated as "A/B". These are different from the usual MAIN, ZONE2, ZONE3 and ZONE4 subunits.

There seem to be 2 variations.

### Speakersets

Zone A/B are just "speakersets" where A is the normal set of speakers and B is an additional set. These can be toggled on/off individually. These are part of the MAIN zone.

On the API, these are controlled with these functions `@MAIN:SPEAKERA` and `@MAIN:SPEAKERB`.

e.g. RX-V573?


### Subzone

Another variation seen on RX-V583 is a "subzone" called Zone B. In the AV Controller app it is shown similar to Zone 2.
This zone can be powered individually from the MAIN zone, but will always have the same input as the MAIN zone.

Reason for calling it a subzone is that its functions are exposed on the MAIN subunit.

On the API, this subzone is controlled by the following functions. Note that Mute only supports On/Off, not the attenuated ones on the main Mute
```
@MAIN:PWRB
@MAIN:ZONEBAVAIL
@MAIN:ZONEBNAME   # Unknown if this can actually be set on the AVR
@MAIN:ZONEBMUTE
@MAIN:ZONEBVOL
```

Note that this variant also has the `@MAIN:SPEAKERA/B` functions. But when controlling the SPEAKERB it will power on/off ZoneB (assumption is that it works the same for SPEAKERA/MAIN zone PWR). So when implementing a client these should probably be hidden/ignored.

## BASIC Response

The BASIC response returns a lot of values with 1 request which is nice to speed up things.
However the set of values that comes back is not stable between receivers.

Initially it was assumed that it would always respond with all supported features.
But at least for PUREDIRMODE this is not the case. It is supported on RX-V1067, but not part of BASIC response.

## Pure Direct mode

There seem to be 2 ways to control PureDirect mode.
Both ways seem to support `On` and `Off`. Unclear why there are 2 ways or to which models it applies.

```
@MAIN:PUREDIRMODE=?  e.g. RX-A810
@MAIN:DIRMODE=?  e.g. RX-V473
```

Both seem to be part of BASIC. Except for RX-V1067 wher PUREDIRMODE is supportec, but not in BASIC.

This was brought up in https://github.com/mvdwetering/yamaha_ynca/discussions/340
