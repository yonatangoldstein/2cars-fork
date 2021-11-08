import datetime
import json
import random
import time
import arcade
import pathlib
from car import CarLanes
from car_config import get_car
from round_config import RoundConfig
from obstacles import Bomb, Star

NUM_OF_CARS = 2
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
CAR_TO_ROAD_LEN_PROPORTION = 0.07

EASY_SPAWN_RATE = 1
MEDIUM_SPAWN_RATE = 0.7
HARD_SPAWN_RATE = 0.5
ROUND_DURATION = 60

MAX_DISTANCE = 100
# The car center_y is exactly one car length away from the bottom of the screen TODO: make this less hard-coded
DISTANCE_TO_CAR = MAX_DISTANCE - MAX_DISTANCE * CAR_TO_ROAD_LEN_PROPORTION * 1.5
DISTANCE_PAST_CAR = MAX_DISTANCE - MAX_DISTANCE * CAR_TO_ROAD_LEN_PROPORTION / 2
OBSTACLE_INITIAL_DISTANCE = 5
OBSTACLE_SPEED = 40
FAILURE_MESSAGE_DISPLAY_TIME = 0.4


class Game2Cars(arcade.Window):
    def __init__(self, width, height, round_configs):
        super().__init__(width, height)
        self._round_index = 0
        self._round_configs = round_configs
        self._round_config = None
        self._cars = []
        self._road_width = 0
        self._lane_line_width = 0
        self._is_started = False
        self._start_time = None
        self._round_start_times = []
        self._round_end_times = []
        self._last_spawn_times = []
        self._obstacles = []
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

        for i in range(self._round_config.num_of_cars):
            road_center_x = (i + 1) * (self.width / (self._round_config.num_of_cars + 1))
            self._draw_road(road_center_x)
            self._draw_car(road_center_x, self._cars[i])
            self._draw_obstacles(road_center_x, self._obstacles[i])

        self._draw_messages()

    def _draw_messages(self):
        last_crash_time = self._crashes[-1] if self._crashes else 0
        if time.time() - last_crash_time < FAILURE_MESSAGE_DISPLAY_TIME:
            arcade.draw_text("Crashed!", self.width / 3, self.height / 2, arcade.color.RED, 32, bold=True)
        last_miss_time = self._misses[-1] if self._misses else 0
        if time.time() - last_miss_time < FAILURE_MESSAGE_DISPLAY_TIME:
            arcade.draw_text("Missed star!", self.width / 3, self.height / 2, arcade.color.YELLOW_ORANGE, 32, bold=True)

    def _draw_intro(self):
        if self._round_index == 0:
            text = "Press space to start"
        elif self._round_index < len(self._round_configs):
            text = "Round over!\nPress space to start the next"
        else:
            text = "All done! thank you for participating :)"
        arcade.draw_text(text, self.width * 0.2, self.height / 2, arcade.color.WHITE_SMOKE, 24,
                         multiline=True, width=self.width)

    def _draw_road(self, center_x):
        arcade.draw_rectangle_filled(center_x, self.height / 2, self._road_width, self.height,
                                     arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_rectangle_filled(center_x, self.height / 2, self._lane_line_width, self.height,
                                     arcade.color.WHITE_SMOKE)

    def _draw_car(self, road_center_x, car):
        car_height = self.height * CAR_TO_ROAD_LEN_PROPORTION
        car_width = car_height / 1.5
        car_center_x = road_center_x + ((self._road_width / 4) * (1 if car.lane == CarLanes.RIGHT else -1))
        arcade.draw_rectangle_filled(car_center_x, car_height, car_width, car_height, car.color)

    def _draw_obstacles(self, road_center_x, obstacles):
        for obstacle in obstacles:
            center_x = road_center_x + ((self._road_width / 4) * (1 if obstacle.lane == CarLanes.RIGHT else -1))
            center_y = self.height * ((MAX_DISTANCE - obstacle.distance) / MAX_DISTANCE)
            arcade.draw_circle_filled(center_x, center_y, self._road_width * CAR_TO_ROAD_LEN_PROPORTION * 1.2, obstacle.color)

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        if not self._is_started:
            return
        if time.time() - self._start_time > self._round_config.duration:
            self._end_round()
            return
        self._move_obstacles(delta_time)
        self._obstacle_car_interactions()
        self._remove_finished_obstacles()
        self._spawn_new_obstacles()

    def _obstacle_car_interactions(self):
        for i in range(self._round_config.num_of_cars):
            for obstacle in self._obstacles[i]:
                if DISTANCE_TO_CAR <= obstacle.distance < DISTANCE_PAST_CAR and obstacle.lane == self._cars[i].lane:
                    if isinstance(obstacle, Bomb):
                        self._handle_crash()
                    self._obstacles[i].remove(obstacle)

    def _remove_finished_obstacles(self):
        for i in range(self._round_config.num_of_cars):
            for obstacle in self._obstacles[i]:
                if obstacle.distance >= MAX_DISTANCE:
                    if isinstance(obstacle, Star):
                        self._handle_miss()
                    self._obstacles[i].remove(obstacle)

    def _handle_crash(self):
        self._crashes.append(time.time())

    def _handle_miss(self):
        self._misses.append(time.time())

    def _move_obstacles(self, delta_time):
        for i in range(self._round_config.num_of_cars):
            for obstacle in self._obstacles[i]:
                obstacle.distance += delta_time * self._round_config.obstacle_speed

    def _spawn_new_obstacles(self):
        for i in range(self._round_config.num_of_cars):
            if time.time() - self._last_spawn_times[i] > (self._round_config.spawn_rate + (random.random() / 5)):
                obstacle_type = Bomb if random.randint(0, 1) == 0 else Star
                lane = CarLanes.LEFT if random.randint(0, 1) == 0 else CarLanes.RIGHT
                self._obstacles[i].append(obstacle_type(lane, OBSTACLE_INITIAL_DISTANCE))
                self._last_spawn_times[i] = time.time()

    def on_key_press(self, symbol: int, modifiers: int):
        for car in self._cars:
            if symbol in car.keymap:
                car.lane = car.keymap[symbol]
        if symbol == arcade.key.SPACE and not self._is_started and self._round_index < len(self._round_configs):
            self._start_round()

    def _end_round(self):
        self._round_end_times.append(time.time())
        self._is_started = False
        self._round_index += 1

    def _start_round(self):
        self._round_config = self._round_configs[self._round_index]
        self._cars = [get_car(i) for i in range(self._round_config.num_of_cars)]
        self._road_width = self.width / self._round_config.num_of_cars / 2
        self._lane_line_width = self._road_width / 20
        self._last_spawn_times = [time.time() for _ in range(self._round_config.num_of_cars)]
        self._obstacles = [[] for _ in range(self._round_config.num_of_cars)]
        self._start_time = time.time()
        self._round_start_times.append(time.time())
        self._is_started = True

    def export_game_data(self):
        return json.dumps({"start_times": self._round_start_times,
                           "crashes": self._crashes,
                           "misses": self._misses,
                           "end_times": self._round_end_times})


def main():
    round_configs = [RoundConfig(NUM_OF_CARS, MEDIUM_SPAWN_RATE, OBSTACLE_SPEED, ROUND_DURATION),
                     RoundConfig(NUM_OF_CARS, HARD_SPAWN_RATE, OBSTACLE_SPEED, ROUND_DURATION)]
    game = Game2Cars(SCREEN_WIDTH, SCREEN_HEIGHT, round_configs)
    game.setup()
    arcade.run()
    pathlib.Path("data").mkdir(exist_ok=True)
    data_filename = "2cars_data_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"
    open(str(pathlib.Path("data", data_filename)), "w").write(game.export_game_data())


if __name__ == "__main__":
    main()
