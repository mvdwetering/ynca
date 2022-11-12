from unittest import mock
from ynca.constants import Playback

from ynca.subunits.function_mixins import (
    PlaybackFunctionMixin,
)


def test_playback():
    class PlaybackFunction(PlaybackFunctionMixin, mock.Mock):
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
