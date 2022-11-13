from ynca import SoundPrg
from ynca.modelinfo import get_modelinfo, ModelInfo


def test_no_modelinfo():
    assert get_modelinfo("unknown") is None


def test_modelinfo():
    rx2000 = get_modelinfo("RX-A2000")
    assert isinstance(rx2000, ModelInfo)
    assert SoundPrg.CHURCH_IN_FREIBURG in rx2000.soundprg

    rx2020 = get_modelinfo("RX-A2020")
    assert SoundPrg.SEVEN_CH_STEREO not in rx2020.soundprg
    assert SoundPrg.NINE_CH_STEREO in rx2020.soundprg
