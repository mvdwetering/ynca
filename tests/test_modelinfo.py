from ynca import SoundPrg, YncaModelInfo


def test_no_modelinfo() -> None:
    assert YncaModelInfo.get("unknown") is None


def test_modelinfo() -> None:
    rx2000 = YncaModelInfo.get("RX-A2000")
    assert rx2000 is not None
    assert SoundPrg.CHURCH_IN_FREIBURG in rx2000.soundprg

    rx2020 = YncaModelInfo.get("RX-A2020")
    assert rx2020 is not None
    assert SoundPrg.SEVEN_CH_STEREO not in rx2020.soundprg
    assert SoundPrg.NINE_CH_STEREO in rx2020.soundprg
