

class CarLanes:
    LEFT = "left"
    RIGHT = "right"


class Car(object):
    def __init__(self, color, keymap, lane=CarLanes.LEFT):
        self._color = color
        self._keymap = keymap
        self._lane = lane

    @property
    def color(self):
        return self._color

    @property
    def keymap(self):
        return self._keymap

    @property
    def lane(self):
        return self._lane

    @lane.setter
    def lane(self, lane):
        self._lane = lane
