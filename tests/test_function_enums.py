"""Test Enums"""


from ynca.constants import Subunit
from ynca.function_enums import (
    Avail,
    DabAudioMode,
    DabOffAir,
    FmSigStereoMono,
    FmTuned,
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
    SigStereoMono,
    SoundPrg,
    Straight,
    Tuned,
    TwoChDecoder,
)


def test_invalid_values_on_enums():
    assert Avail("x") is Avail.UNKNOWN
    assert DabAudioMode("x") is DabAudioMode.UNKNOWN
    assert DabOffAir("x") is DabOffAir.UNKNOWN
    assert FmSigStereoMono("x") is FmSigStereoMono.UNKNOWN
    assert FmTuned("x") is FmTuned.UNKNOWN
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
    assert SigStereoMono("x") is SigStereoMono.UNKNOWN
    assert SoundPrg("x") is SoundPrg.UNKNOWN
    assert Straight("x") is Straight.UNKNOWN
    assert Tuned("x") is Tuned.UNKNOWN
    assert TwoChDecoder("x") is TwoChDecoder.UNKNOWN


def test_invalid_values_on_subunit():
    assert Subunit("x") is Subunit.UNKNOWN
