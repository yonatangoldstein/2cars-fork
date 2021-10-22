import arcade

NUM_OF_CARS = 2
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

class CarLanes:
    LEFT = "left"
    RIGHT = "right"

class Game2Cars(arcade.Window):
    def __init__(self, width, height, num_of_cars):
        super().__init__(width, height)
        self._num_of_cars = num_of_cars
        self._car_lanes = [CarLanes.LEFT for _ in range(num_of_cars)]
        self._road_width = width / num_of_cars / 2
        self._lane_line_width = self._road_width / 20
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        pass

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        self._draw_roads()

    def _draw_roads(self):
        for i in range(self._num_of_cars):
            road_center_x = (i + 1) * (self.width / (self._num_of_cars + 1))
            self._draw_road(road_center_x)
            self._draw_car(road_center_x, self._car_lanes[i])

    def _draw_road(self, center_x):
        arcade.draw_rectangle_filled(center_x, self.height / 2, self._road_width, self.height,
                                     arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_rectangle_filled(center_x, self.height / 2, self._lane_line_width, self.height,
                                     arcade.color.WHITE_SMOKE)

    def _draw_car(self, road_center_x, car_lane):
        car_width = self._road_width / 3.5
        car_height = self.height / 10
        car_center_x = road_center_x + ((self._road_width / 4) * (1 if car_lane == CarLanes.RIGHT else -1))
        arcade.draw_rectangle_filled(car_center_x, car_height, car_width, car_height, arcade.color.REDWOOD)

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        pass

    def on_key_press(self, symbol: int, modifiers: int):
        if symbol == arcade.key.LEFT:
            self._car_lanes[1] = CarLanes.LEFT
        elif symbol == arcade.key.RIGHT:
            self._car_lanes[1] = CarLanes.RIGHT


def main():
    game = Game2Cars(SCREEN_WIDTH, SCREEN_HEIGHT, NUM_OF_CARS)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
