"""Test Enums"""


from ynca.enums import (
    AdaptiveDrc,
    Avail,
    BandDab,
    BandTun,
    Enhancer,
    HdmiOut,
    HdmiOutOnOff,
    InitVolLvl,
    InitVolMode,
    Input,
    Mute,
    Party,
    PartyMute,
    Playback,
    PlaybackInfo,
    PureDirMode,
    Pwr,
    Repeat,
    Shuffle,
    Sleep,
    SoundPrg,
    Straight,
    ThreeDeeCinema,
    TwoChDecoder,
)


def test_invalid_values_on_enums():
    assert AdaptiveDrc("x") is AdaptiveDrc.UNKNOWN
    assert Avail("x") is Avail.UNKNOWN
    assert BandDab("x") is BandDab.UNKNOWN
    assert BandTun("x") is BandTun.UNKNOWN
    assert Enhancer("x") is Enhancer.UNKNOWN
    assert HdmiOut("x") is HdmiOut.UNKNOWN
    assert HdmiOutOnOff("x") is HdmiOutOnOff.UNKNOWN
    assert InitVolLvl("x") is InitVolLvl.UNKNOWN
    assert InitVolMode("x") is InitVolMode.UNKNOWN
    assert Input("x") is Input.UNKNOWN
    assert Mute("x") is Mute.UNKNOWN
    assert Party("x") is Party.UNKNOWN
    assert PartyMute("x") is PartyMute.UNKNOWN
    assert Playback("x") is Playback.UNKNOWN
    assert PlaybackInfo("x") is PlaybackInfo.UNKNOWN
    assert PureDirMode("x") is PureDirMode.UNKNOWN
    assert Pwr("x") is Pwr.UNKNOWN
    assert Repeat("x") is Repeat.UNKNOWN
    assert Shuffle("x") is Shuffle.UNKNOWN
    assert Sleep("x") is Sleep.UNKNOWN
    assert SoundPrg("x") is SoundPrg.UNKNOWN
    assert Straight("x") is Straight.UNKNOWN
    assert ThreeDeeCinema("x") is ThreeDeeCinema.UNKNOWN
    assert TwoChDecoder("x") is TwoChDecoder.UNKNOWN
