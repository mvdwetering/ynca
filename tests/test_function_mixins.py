"""Test Function mixins"""

from unittest import mock
from ynca.constants import Playback, PlaybackInfo

from ynca.function_mixins import PlaybackFunctionMixin, PlaybackInfoFunctionMixin


def test_playback():
    class PlaybackFunction(PlaybackFunctionMixin, mock.MagicMock):
        pass

    pf = PlaybackFunction()

    pf.playback(Playback.PLAY)
    pf._put.assert_called_with("PLAYBACK", "Play")
    pf.playback(Playback.PAUSE)
    pf._put.assert_called_with("PLAYBACK", "Pause")
    pf.playback(Playback.STOP)
    pf._put.assert_called_with("PLAYBACK", "Stop")
    pf.playback(Playback.SKIP_FWD)
    pf._put.assert_called_with("PLAYBACK", "Skip Fwd")
    pf.playback(Playback.SKIP_REV)
    pf._put.assert_called_with("PLAYBACK", "Skip Rev")


def test_playbackinfo():
    class PlaybackInfoFunction(PlaybackInfoFunctionMixin):
        pass

    pif = PlaybackInfoFunction()
    pif._attr_playbackinfo = "Play"
    assert pif.playbackinfo is PlaybackInfo.PLAY
    pif._attr_playbackinfo = "Pause"
    assert pif.playbackinfo is PlaybackInfo.PAUSE
    pif._attr_playbackinfo = "Stop"
    assert pif.playbackinfo is PlaybackInfo.STOP
