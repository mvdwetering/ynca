from ynca import SoundPrg, YncaModelInfo


def test_no_modelinfo():
    assert YncaModelInfo.get("unknown") is None


def test_modelinfo():
    rx2000 = YncaModelInfo.get("RX-A2000")
    assert SoundPrg.CHURCH_IN_FREIBURG in rx2000.soundprg

    rx2020 = YncaModelInfo.get("RX-A2020")
    assert SoundPrg.SEVEN_CH_STEREO not in rx2020.soundprg
    assert SoundPrg.NINE_CH_STEREO in rx2020.soundprg
