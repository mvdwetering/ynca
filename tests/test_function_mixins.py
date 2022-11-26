from unittest import mock
from ynca import Playback

from ynca.subunits.functions import (
    PlaybackFunction,
)


def test_playback():
    class WithPlaybackFunction(PlaybackFunction, mock.Mock):
        pass

    wpf = WithPlaybackFunction()

    wpf.playback(Playback.PLAY)
    wpf._put.assert_called_with("PLAYBACK", "Play")
    wpf.playback(Playback.PAUSE)
    wpf._put.assert_called_with("PLAYBACK", "Pause")
    wpf.playback(Playback.STOP)
    wpf._put.assert_called_with("PLAYBACK", "Stop")
    wpf.playback(Playback.SKIP_FWD)
    wpf._put.assert_called_with("PLAYBACK", "Skip Fwd")
    wpf.playback(Playback.SKIP_REV)
    wpf._put.assert_called_with("PLAYBACK", "Skip Rev")
