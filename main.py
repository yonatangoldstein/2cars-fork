import arcade
from car import CarLanes
from car_config import get_car

NUM_OF_CARS = 2
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600


class Game2Cars(arcade.Window):
    def __init__(self, width, height, num_of_cars):
        super().__init__(width, height)
        self._num_of_cars = num_of_cars
        self._cars = [get_car(i) for i in range(num_of_cars)]
        self._road_width = width / num_of_cars / 2
        self._lane_line_width = self._road_width / 20
        self._is_started = False
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

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        for car in self._cars:
            if symbol in car.keymap:
                car.lane = car.keymap[symbol]
        if symbol == arcade.key.SPACE and not self._is_started:
            self._start_game()

    def _start_game(self):
        self._is_started = True


def main():
    game = Game2Cars(SCREEN_WIDTH, SCREEN_HEIGHT, NUM_OF_CARS)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
