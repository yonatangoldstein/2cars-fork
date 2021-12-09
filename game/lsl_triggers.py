from pylsl import StreamInfo, StreamOutlet


ROUND_BEGIN_TRIGGER = 100
SPAWN_BEGIN_TRIGGER = 111
ROUND_END_TRIGGER = 101

MISTAKE_TRIGGER = 404


class LslTriggers(object):
    """
    An interface to mark events to lsl stream
    """
    def __init__(self):
        self._outlet = StreamOutlet(StreamInfo("GameMarkers", "Markers"))

    def mark_round_start(self):
        self._outlet.push_sample([ROUND_BEGIN_TRIGGER])

    def mark_spawn_start(self):
        self._outlet.push_sample([SPAWN_BEGIN_TRIGGER])

    def mark_round_end(self):
        self._outlet.push_sample([ROUND_END_TRIGGER])

    def mark_mistake(self):
        self._outlet.push_sample([MISTAKE_TRIGGER])
