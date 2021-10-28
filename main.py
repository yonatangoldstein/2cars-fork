import datetime
import json
import random
import time
import arcade
from car import CarLanes
from car_config import get_car
from obstacles import Bomb, Star

NUM_OF_CARS = 2
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
SPAWN_RATE = 1
MAX_DISTANCE = 100
DISTANCE_TO_CAR = 84
DISTANCE_PAST_CAR = 97
OBSTACLE_INITIAL_DISTANCE = 5
OBSTACLE_SPEED = 0.5
FAILURE_MESSAGE_DISPLAY_TIME = 0.4


class Game2Cars(arcade.Window):
    def __init__(self, width, height, num_of_cars, spawn_rate):
        super().__init__(width, height)
        self._num_of_cars = num_of_cars
        self._cars = [get_car(i) for i in range(num_of_cars)]
        self._road_width = width / num_of_cars / 2
        self._lane_line_width = self._road_width / 20
        self._is_started = False
        self._start_time = None
        self._last_spawn_times = [0.0 for _ in range(num_of_cars)]
        self._obstacles = [[] for _ in range(num_of_cars)]
        self._spawn_rate = spawn_rate
        self._misses = []
        self._crashes = []
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        pass

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        if not self._is_started:
            self._draw_intro()
            return

        for i in range(self._num_of_cars):
            road_center_x = (i + 1) * (self.width / (self._num_of_cars + 1))
            self._draw_road(road_center_x)
            self._draw_car(road_center_x, self._cars[i])
            self._draw_obstacles(road_center_x, self._obstacles[i])

        self._draw_failure_messages()

    def _draw_failure_messages(self):
        last_crash_time = self._crashes[-1] if self._crashes else 0
        if time.time() - last_crash_time < FAILURE_MESSAGE_DISPLAY_TIME:
            arcade.draw_text("Crashed!", self.width / 3, self.height / 2, arcade.color.RED, 32, bold=True)
        last_miss_time = self._misses[-1] if self._misses else 0
        if time.time() - last_miss_time < FAILURE_MESSAGE_DISPLAY_TIME:
            arcade.draw_text("Missed star!", self.width / 3, self.height / 2, arcade.color.YELLOW_ORANGE, 32, bold=True)

    def _draw_intro(self):
        arcade.draw_text("Press space to start", self.width * 0.2, self.height / 2, arcade.color.WHITE_SMOKE, 24)

    def _draw_road(self, center_x):
        arcade.draw_rectangle_filled(center_x, self.height / 2, self._road_width, self.height,
                                     arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_rectangle_filled(center_x, self.height / 2, self._lane_line_width, self.height,
                                     arcade.color.WHITE_SMOKE)

    def _draw_car(self, road_center_x, car):
        car_width = self._road_width / 3.5
        car_height = self.height / 10
        car_center_x = road_center_x + ((self._road_width / 4) * (1 if car.lane == CarLanes.RIGHT else -1))
        arcade.draw_rectangle_filled(car_center_x, car_height, car_width, car_height, car.color)

    def _draw_obstacles(self, road_center_x, obstacles):
        for obstacle in obstacles:
            center_x = road_center_x + ((self._road_width / 4) * (1 if obstacle.lane == CarLanes.RIGHT else -1))
            center_y = self.height * ((MAX_DISTANCE - obstacle.distance) / MAX_DISTANCE)
            arcade.draw_circle_filled(center_x, center_y, self._road_width / 7, obstacle.color)

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        if not self._is_started:
            return
        self._move_obstacles()
        self._obstacle_car_interactions()
        self._remove_finished_obstacles()
        self._spawn_new_obstacles()

    def _obstacle_car_interactions(self):
        for i in range(self._num_of_cars):
            for obstacle in self._obstacles[i]:
                if DISTANCE_TO_CAR <= obstacle.distance < DISTANCE_PAST_CAR and obstacle.lane == self._cars[i].lane:
                    if isinstance(obstacle, Bomb):
                        self._handle_crash()
                    self._obstacles[i].remove(obstacle)

    def _remove_finished_obstacles(self):
        for i in range(self._num_of_cars):
            for obstacle in self._obstacles[i]:
                if obstacle.distance >= MAX_DISTANCE:
                    if isinstance(obstacle, Star):
                        self._handle_miss()
                    self._obstacles[i].remove(obstacle)

    def _handle_crash(self):
        self._crashes.append(time.time())

    def _handle_miss(self):
        self._misses.append(time.time())

    def _move_obstacles(self):
        for i in range(self._num_of_cars):
            for obstacle in self._obstacles[i]:
                obstacle.distance += OBSTACLE_SPEED

    def _spawn_new_obstacles(self):
        for i in range(self._num_of_cars):
            if time.time() - self._last_spawn_times[i] > (self._spawn_rate + (random.random() / 5)):
                obstacle_type = Bomb if random.randint(0, 1) == 0 else Star
                lane = CarLanes.LEFT if random.randint(0, 1) == 0 else CarLanes.RIGHT
                self._obstacles[i].append(obstacle_type(lane, OBSTACLE_INITIAL_DISTANCE))
                self._last_spawn_times[i] = time.time()

    def on_key_press(self, symbol: int, modifiers: int):
        for car in self._cars:
            if symbol in car.keymap:
                car.lane = car.keymap[symbol]
        if symbol == arcade.key.SPACE and not self._is_started:
            self._start_game()

    def _start_game(self):
        self._is_started = True
        self._start_time = time.time()

    def export_game_data(self):
        return json.dumps({"start_time": self._start_time,
                           "crashes": self._crashes,
                           "misses": self._misses})


def main():
    game = Game2Cars(SCREEN_WIDTH, SCREEN_HEIGHT, NUM_OF_CARS, SPAWN_RATE)
    game.setup()
    arcade.run()
    data_filename = "2cars_data_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"
    open(data_filename, "w").write(game.export_game_data())


if __name__ == "__main__":
    main()
