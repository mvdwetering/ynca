# Practicalities

This document describes some notes on weirdness/unexpected behaviour and other practicalities found when working with devices using the YNCA protocol in general, so not limited to this library, but also (potential) usecases for this library.

## Fixed volume

Sometimes zones report values for volume and allow setting it, but it does not take effect.
There are also no response/updates on trying to change the volume (as it is fixed).

For reference, on my RX-A810 with firmware 1.80/2.01, the AV Control Android app also shows volume controls for Zone2 which do not work.
The webinterface on the receiver however shows the text "FIXED" for the volume on Zone2

This is most likely related to the speakerconfiguration indicated by the `@SYS:SPPATTERN1AMP` function (or `@SYS:SPPATTERN2AMP` if the receiver supports multiple speaker patterns).
This function can have values like `Basic`, `ZoneB`, `7ch +1ZONE`, `5ch BI-AMP` and many more.
My initial guess was that when `+1ZONE` is there that means that actual speakers for Zone2 are connected and on the `Basic` case you are supposed to use the preout connections for Zone2.
And with a `+2ZONE` it would be Zone 2 and Zone 3.

However it is a bit more subtle. For example the RX-A2010 manual tells the following about `7ch +1ZONE` configuration:

> Select this when you use 7-channel speakers in the main zone and Zone2 (or Zone3) speakers (p.24).
> You can select a zone to be assigned to the EXTRA SP1 jacks (default: Zone2).

I could not find a function that indicates which Zone is assigned and I don't have a receiver with this feature to experiment with.

Next to that there is `ZoneB` which is a configuration with additional speakers with their own volume control, but same input as Main zone. So not +1ZONE in the name, but does have actual volume control. But then again ZoneB is not a real zone, it is a "subzone" of MAIN.

Would be nice to properly detect this for Home Assistant so the mediaplayer can hide the volume controls.

## Scene activation not working

For some receivers activating scenes does not work and they answer with @RESTRICTED.
See <https://github.com/mvdwetering/yamaha_ynca/issues/19> for logs.

Currently known receivers that behave like this:

* RX-V475 1.34/2.06 (probably also RX-V575/HTR-4066/HTR-5066 because they share the same firmware)

As a workaround the remote codes for SCENE1 etc... can be sent. This works at least on RX-V475 based on user feedback.

## No Zone and Scene names

Some receivers respond with @UNDEFINED for ZONENAME and SCENENAME requests.
Strange part is that the user seems to be able to change names on the receiver (or only in the app?), but that info is not available through YNCA.
See <https://github.com/mvdwetering/yamaha_ynca/issues/8> for logs

Currently known receivers that behave like this:

* TSR-700 1.53/3.12
* RX-A6A 1.80/3.12

So maybe this is "feature" of the 3.x protocol version?

## INITVOLLVL variations

Some receivers report "Off" as value for INITVOLLVL while others (most?) have a specific INITVOLLVLMODE to turn it on/off.
Presumaby receivers that report "Off" have the INITVOLLVL and INITVOLLVLMODE combined.

So assumed functionality is:

* "Off" = Disabled (a.k.a. last state)
* "Mute" = Enabled with Mute
* number = Enabled with specific level

Currently known receivers that can report "Off":

* RX-V477 1.28/1.4

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

### SYS:HDMIOUT1/2/3

This seems to be for newer receivers like TSR-700 and RX-A6A

SYS:HDMIOUT# is a boolean that can have values On and Off. This command toggles a specific HDMIOUT on/off.

This command has been seen for HDMIOUT 1, 2 and 3.

What makes this command a bit weird is while it is part of the SYS subunit it can _only_ be controlled when the related zone is On. So for example you can only control HDMIOUT1 when the MAIN zone is On. See logging in [this discussion comment](https://github.com/mvdwetering/yamaha_ynca/discussions/119#discussioncomment-6103924)

That seems workable for HDMIOUT 1 and 2 since those always seem to be related to the MAIN zone, but HDMIOUT3 is special and can be linked with ZONE2 and ZONE4 on an RX-A4A or RX-A6A according to the manual. It is unknown if/how it is possible to figure out to which zone it is configured. Would need logging when changing that setting.

In RX-A6A logging (see logs directory) it seems like both zones (2 and 4) report HDMIOUT3 as a result of requesting BASIC.

## AUDIO input

Some receivers have a single audio input and that input is called AUDIO. Receivers with multiple audio inputs have them called AUDIO1, AUDIO2 etc...

Seen on RX-V475 receiver in [issue #230](https://github.com/mvdwetering/yamaha_ynca/issues/230), but probably also applies to RX-V575/HTR-4066/HTR-5066 as they share the same firmware.

For some reason this input is _not_ reported when requesting the input names with `@SYS:INPNAME=?` (unlike AUDIO1, AUDIO2 inputs). This makes it impossible to automatically detect if the input is supported by the receiver. The receiver does respond with `@RESTRICTED` when requesting `@SYS:INPNAMEAUDIO1=?` or `@SYS:TRIG1INPAUDIO1=?` instead of `@UNDEFINED`. However these responses are currently not really handled by the library. ~~Building support for that will be hard as there is not a guarenteed request/response mechanism due to the asynchronous nature of the protocol~~ (not true, a GET will result in a response or error).

## Zone A/B receivers

(this section is compiled from findings in <https://github.com/mvdwetering/yamaha_ynca/issues/320>)

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

```text
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

## (Pure) Direct mode

Turns out there are 2 direct modes; Direct and Pure Direct.

These are slightly different. Pure Direct bypasses more signal processing than Direct does.
It seems Pure Direct is an evolution of Direct because Direct seems to apply to older/lower end models.

Both commands support `On` and `Off`.

```text
@MAIN:PUREDIRMODE=?  e.g. RX-A810
@MAIN:DIRMODE=?  e.g. RX-V473
```

Both seem to be part of BASIC. Except for RX-V1067 where PUREDIRMODE is supported, but not in BASIC.

It turns out that DIRMODE does _not_ respond with the new state on state changes.
At least on RX-V473 with firmware 1.23/1.04. You still get STRAIGHT updates though which is related to DIRMODE.

## Presets

Which subunits support Presets varies by model.

All models seem to support Preset for the tuner subunit (AM/FM/DAB).

Some, seemingly older (pre 2012?), models like my RX-A810 supports them also for several other subunits like Napster, Netradio, Pandora, PC, Rhapsody, Sirius, SiriusIR and USB.
Newer(?) models don't seem to support presets for those subunits. Doing a GET for PRESET results in @RESTRICTED on subunits that do not support it (which is expected, but impossible to relate to the GET in current architecture).
On my RX-A810 the receiver does not respond at all on that command.I guess that this is because the additional subunits don't have actual numerical preset values.
More details see <https://github.com/mvdwetering/yamaha_ynca/issues/379>

## Shuffle and repeat updates

Normally when setting a value different from its current value an event is generated from the receiver. However this is not the case for TIDAL (and probably Deezer) source on CX-A5100 where no update seems to be sent. When changing shuffle/repeat from TIDAL side there are updates being sent. I am assuming that it is a bug in the receiver, either just for these sources or that model.

See the logs in <https://github.com/mvdwetering/yamaha_ynca/issues/441> for more details.

NOTE that later logs in the linked issue seem to properly give responses for shuffle and repeat when values are changed. Unclear what happened. The workaround to manually request status after changing it in the HA integration might not be needed.

## Repeat mode rename

In the logs from a CX-A5100 it was observed that setting repeat mode `Single` resulted in an `@UNDEFINED` error. Later in the logs the user sets repeat modes through other means and it reports mode `One`.

Based on this info it seems that `Single` got renamed to `One`.

Only seen this value on the TIDAL source on CX-A5100. Presumably it is the same for all sources on that model. This receiver also had protocol version 2.86/4.41, so it is assumed to be part of version 4 of the protocol.

For logs see: <https://github.com/mvdwetering/yamaha_ynca/issues/441#issuecomment-3520099036>
