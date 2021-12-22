import datetime
import json
import random
import time
import arcade
import pathlib
from car import CarLanes
from car_config import get_car
from game.colors import luminance, adjust_color_to_match_luminance
from round_config import RoundConfig
from obstacles import Bomb, Star
from game.lsl_triggers import LslTriggers

NUM_OF_CARS = 2
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 750
CAR_TO_ROAD_LEN_PROPORTION = 0.07

EASY_SPAWN_RATE = 2.5
MEDIUM_SPAWN_RATE = 1
HARD_SPAWN_RATE = 0.4
IMPROVEMENT_BLOCK_SPAWN_RATE = 0.6
IMPROVEMENT_BLOCK_DURATION = 60
TRAINING_BLOCK_DURATION = 30

MAX_DISTANCE = 100
# The car center_y is exactly one car length away from the bottom of the screen TODO: make this less hard-coded
DISTANCE_TO_CAR = MAX_DISTANCE - MAX_DISTANCE * CAR_TO_ROAD_LEN_PROPORTION * 1.5
DISTANCE_PAST_CAR = MAX_DISTANCE - MAX_DISTANCE * CAR_TO_ROAD_LEN_PROPORTION / 2
OBSTACLE_INITIAL_DISTANCE = 5
OBSTACLE_SPEED = 40
FAILURE_MESSAGE_DISPLAY_TIME = 0.4
COUNTDOWN_DURATION = 5
BACKGROUND_COLOR = arcade.color.AMAZON
ROAD_COLOR = arcade.color.ASH_GREY
LANE_LINE_COLOR = arcade.color.WHITE_SMOKE


class Game2Cars(arcade.Window):
    def __init__(self, width, height, round_configs, lsl_trigger=None):
        super().__init__(width, height)
        self._round_index = 0
        self._round_configs = round_configs
        self._round_config = None
        self._cars = []
        self._road_width = 0
        self._lane_line_width = 0
        self._car_width = 0
        self._car_height = 0
        self._message_color = None
        self._countdown_color = None
        self._bomb_color = None
        self._star_color = None
        self._is_started = False
        self._is_spawn_started = False
        self._start_time = None
        self._round_start_times = []
        self._spawn_start_times = []
        self._round_end_times = []
        self._last_spawn_times = []
        self._obstacles = []
        self._misses = []
        self._crashes = []
        self._lsl_trigger = lsl_trigger
        arcade.set_background_color(BACKGROUND_COLOR)

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

        if not self._is_spawn_started:
            self._draw_countdown()

        self._draw_messages()

    def _draw_countdown(self):
        count = self._round_config.countdown_duration - int(time.time() - self._start_time)
        arcade.draw_text("Get ready", self.width * 0.37, self.height * 2 / 3, self._countdown_color, 34, bold=True)
        arcade.draw_text(str(count), self.width * 0.48, self.height * 1.8 / 3, self._countdown_color, 34, bold=True)

    def _draw_messages(self):
        last_crash_time = self._crashes[-1] if self._crashes else 0
        if time.time() - last_crash_time < FAILURE_MESSAGE_DISPLAY_TIME:
            arcade.draw_text("Crashed!", self.width / 3, self.height / 2, self._message_color, 32, bold=True)
        last_miss_time = self._misses[-1] if self._misses else 0
        if time.time() - last_miss_time < FAILURE_MESSAGE_DISPLAY_TIME:
            arcade.draw_text("Missed star!", self.width / 3, self.height / 2, self._message_color, 32, bold=True)

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
        arcade.draw_rectangle_filled(center_x, self.height / 2, self._road_width, self.height, ROAD_COLOR)
        arcade.draw_rectangle_filled(center_x, self.height / 2, self._lane_line_width, self.height, LANE_LINE_COLOR)

    def _draw_car(self, road_center_x, car):
        car_center_x = road_center_x + ((self._road_width / 4) * (1 if car.lane == CarLanes.RIGHT else -1))
        arcade.draw_rectangle_filled(car_center_x, self._car_height, self._car_width, self._car_height, car.color)

    def _draw_obstacles(self, road_center_x, obstacles):
        for obstacle in obstacles:
            center_x = road_center_x + ((self._road_width / 4) * (1 if obstacle.lane == CarLanes.RIGHT else -1))
            center_y = self.height * ((MAX_DISTANCE - obstacle.distance) / MAX_DISTANCE)
            arcade.draw_circle_filled(center_x, center_y, self._road_width * CAR_TO_ROAD_LEN_PROPORTION * 1.2, obstacle.color)

    def update(self, delta_time):
        if not self._is_started:
            return
        if time.time() - (self._start_time + self._round_config.countdown_duration) > self._round_config.duration:
            self._end_round()
            return
        if not self._is_spawn_started and time.time() - self._start_time > self._round_config.countdown_duration:
            self._start_spawn()
        self._move_obstacles(delta_time)
        self._obstacle_car_interactions()
        self._remove_finished_obstacles()
        if self._is_spawn_started:
            self._spawn_new_obstacles()

    def _start_spawn(self):
        self._spawn_start_times.append(time.time())
        self._lsl_trigger.mark_spawn_start()
        self._is_spawn_started = True

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
        if self._lsl_trigger:
            self._lsl_trigger.mark_mistake()

    def _handle_miss(self):
        self._misses.append(time.time())
        if self._lsl_trigger:
            self._lsl_trigger.mark_mistake()

    def _move_obstacles(self, delta_time):
        for i in range(self._round_config.num_of_cars):
            for obstacle in self._obstacles[i]:
                obstacle.distance += delta_time * self._round_config.obstacle_speed

    def _spawn_new_obstacles(self):
        for i in range(self._round_config.num_of_cars):
            if time.time() - self._last_spawn_times[i] > (self._round_config.spawn_rate + (random.random() / 5)):
                obstacle_type = Bomb if random.randint(0, 1) == 0 else Star
                lane = CarLanes.LEFT if random.randint(0, 1) == 0 else CarLanes.RIGHT
                color = self._star_color if obstacle_type == Star else self._bomb_color
                self._obstacles[i].append(obstacle_type(lane, OBSTACLE_INITIAL_DISTANCE, color))
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
        self._is_spawn_started = False
        self._round_index += 1
        if self._lsl_trigger:
            self._lsl_trigger.mark_round_end()

    def _start_round(self):
        self._round_config = self._round_configs[self._round_index]
        self._cars = [get_car(i) for i in range(self._round_config.num_of_cars)]
        self._road_width = self.width / self._round_config.num_of_cars / 2
        self._lane_line_width = self._road_width / 20
        self._car_height = self.height * CAR_TO_ROAD_LEN_PROPORTION
        self._car_width = self._car_height / 1.5
        self._last_spawn_times = [time.time() for _ in range(self._round_config.num_of_cars)]
        self._obstacles = [[] for _ in range(self._round_config.num_of_cars)]
        self._start_time = time.time()
        self._round_start_times.append(time.time())
        self._is_started = True
        if self._lsl_trigger:
            self._lsl_trigger.mark_round_start()
        self._stabilize_luminance()

    def _stabilize_luminance(self):
        avg_luminance = self._calc_avg_luminance()
        self._message_color = adjust_color_to_match_luminance(list(arcade.color.CHINESE_RED), avg_luminance)
        self._countdown_color = adjust_color_to_match_luminance(list(arcade.color.DEEP_SPACE_SPARKLE), avg_luminance)
        self._bomb_color = adjust_color_to_match_luminance(list(Bomb.base_color()), avg_luminance * 0.5)
        self._star_color = adjust_color_to_match_luminance(list(Star.base_color()), avg_luminance * 1.5)

    def _calc_avg_luminance(self):
        total_area = self.width * self.height
        car_area = self._car_width * self._car_height
        lane_line_area = self._lane_line_width * self.height
        road_area = self._road_width * self.height - lane_line_area - car_area
        background_area = total_area - (road_area + lane_line_area + car_area) * self._round_config.num_of_cars
        avg_luminance = ((background_area / total_area) * luminance(BACKGROUND_COLOR) +
                         (road_area * self._round_config.num_of_cars / total_area) * luminance(ROAD_COLOR) +
                         (lane_line_area * self._round_config.num_of_cars / total_area) * luminance(LANE_LINE_COLOR) +
                         sum((car_area / total_area) * luminance(car.color) for car in self._cars))
        return avg_luminance

    def export_game_data(self):
        return json.dumps({"start_times": self._round_start_times,
                           "spawn_start_times": self._spawn_start_times,
                           "crashes": self._crashes,
                           "misses": self._misses,
                           "end_times": self._round_end_times})


def main():
    round_configs = [RoundConfig(NUM_OF_CARS, HARD_SPAWN_RATE, OBSTACLE_SPEED, TRAINING_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, EASY_SPAWN_RATE, OBSTACLE_SPEED, TRAINING_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, MEDIUM_SPAWN_RATE, OBSTACLE_SPEED, TRAINING_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, HARD_SPAWN_RATE, OBSTACLE_SPEED, TRAINING_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, EASY_SPAWN_RATE, OBSTACLE_SPEED, TRAINING_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, HARD_SPAWN_RATE, OBSTACLE_SPEED, TRAINING_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, MEDIUM_SPAWN_RATE, OBSTACLE_SPEED, TRAINING_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, IMPROVEMENT_BLOCK_SPAWN_RATE, OBSTACLE_SPEED, IMPROVEMENT_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, IMPROVEMENT_BLOCK_SPAWN_RATE, OBSTACLE_SPEED, IMPROVEMENT_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, IMPROVEMENT_BLOCK_SPAWN_RATE, OBSTACLE_SPEED, IMPROVEMENT_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, IMPROVEMENT_BLOCK_SPAWN_RATE, OBSTACLE_SPEED, IMPROVEMENT_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, IMPROVEMENT_BLOCK_SPAWN_RATE, OBSTACLE_SPEED, IMPROVEMENT_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, IMPROVEMENT_BLOCK_SPAWN_RATE, OBSTACLE_SPEED, IMPROVEMENT_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, IMPROVEMENT_BLOCK_SPAWN_RATE, OBSTACLE_SPEED, IMPROVEMENT_BLOCK_DURATION, COUNTDOWN_DURATION),
                     RoundConfig(NUM_OF_CARS, IMPROVEMENT_BLOCK_SPAWN_RATE, OBSTACLE_SPEED, IMPROVEMENT_BLOCK_DURATION, COUNTDOWN_DURATION)]

    # add 2 empty rounds for calibration
    calibration_time = 30
    calibration_round_configs = [RoundConfig(NUM_OF_CARS, 0, 0, 0, calibration_time),
                                 RoundConfig(NUM_OF_CARS, 0, 0, 0, calibration_time)]

    round_configs = calibration_round_configs + round_configs

    game = Game2Cars(SCREEN_WIDTH, SCREEN_HEIGHT, round_configs, LslTriggers())
    arcade.run()
    pathlib.Path("data").mkdir(exist_ok=True)
    data_filename = "2cars_data_" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S") + ".json"
    open(str(pathlib.Path("data", data_filename)), "w").write(game.export_game_data())


if __name__ == "__main__":
    main()
