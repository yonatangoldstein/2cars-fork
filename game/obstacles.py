import arcade


class Obstacle(object):
    def __init__(self, lane, distance):
        self._lane = lane
        self._distance = distance

    @property
    def lane(self):
        return self._lane

    @property
    def distance(self):
        return self._distance

    @distance.setter
    def distance(self, distance):
        self._distance = distance

    @property
    def color(self):
        raise NotImplementedError()


class Bomb(Obstacle):
    @property
    def color(self):
        return arcade.color.BLACK


class Star(Obstacle):
    @property
    def color(self):
        return arcade.color.GOLD
