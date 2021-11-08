

class GameConfig(object):
    def __init__(self, num_of_cars, spawn_rate, obstacle_speed):
        self._num_of_cars = num_of_cars
        self._spawn_rate = spawn_rate
        self._obstacle_speed = obstacle_speed

    @property
    def num_of_cars(self):
        return self._num_of_cars

    @property
    def spawn_rate(self):
        return self._spawn_rate

    @property
    def obstacle_speed(self):
        return self._obstacle_speed
