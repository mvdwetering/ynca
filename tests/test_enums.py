"""Test Enums"""


from ynca.enums import (
    Avail,
    InitVolMode,
    Mute,
    Party,
    PartyMute,
    Playback,
    PlaybackInfo,
    PureDirMode,
    Pwr,
    Repeat,
    Shuffle,
    SoundPrg,
    Straight,
    TwoChDecoder,
)


def test_invalid_values_on_enums():
    assert Avail("x") is Avail.UNKNOWN
    assert InitVolMode("x") is InitVolMode.UNKNOWN
    assert Mute("x") is Mute.UNKNOWN
    assert Party("x") is Party.UNKNOWN
    assert PartyMute("x") is PartyMute.UNKNOWN
    assert Playback("x") is Playback.UNKNOWN
    assert PlaybackInfo("x") is PlaybackInfo.UNKNOWN
    assert PureDirMode("x") is PureDirMode.UNKNOWN
    assert Pwr("x") is Pwr.UNKNOWN
    assert Repeat("x") is Repeat.UNKNOWN
    assert Shuffle("x") is Shuffle.UNKNOWN
    assert SoundPrg("x") is SoundPrg.UNKNOWN
    assert Straight("x") is Straight.UNKNOWN
    assert TwoChDecoder("x") is TwoChDecoder.UNKNOWN
