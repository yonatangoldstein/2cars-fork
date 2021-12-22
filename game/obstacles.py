import arcade


class Obstacle(object):
    def __init__(self, lane, distance, color):
        self._lane = lane
        self._distance = distance
        self._color = color

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
        return self._color

    @classmethod
    def base_color(cls):
        raise NotImplementedError()


class Bomb(Obstacle):
    @classmethod
    def base_color(cls):
        return arcade.color.BLACK


class Star(Obstacle):
    @classmethod
    def base_color(cls):
        return arcade.color.GOLD
