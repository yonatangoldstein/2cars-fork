import arcade

NUM_OF_ROADS = 2
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

ROAD_WIDTH = SCREEN_WIDTH / NUM_OF_ROADS / 2
LANE_LINE_WIDTH = ROAD_WIDTH / 20


class MyGame(arcade.Window):
    def __init__(self, width, height):
        super().__init__(width, height)
        arcade.set_background_color(arcade.color.AMAZON)

    def setup(self):
        pass

    def on_draw(self):
        """ Render the screen. """
        arcade.start_render()
        for i in range(NUM_OF_ROADS):
            road_center_x = (i + 1) * (SCREEN_WIDTH / (NUM_OF_ROADS + 1))
            self.draw_road(road_center_x)

    @staticmethod
    def draw_road(center_x):
        arcade.draw_rectangle_filled(center_x, SCREEN_HEIGHT / 2, ROAD_WIDTH, SCREEN_HEIGHT,
                                     arcade.color.BLACK_LEATHER_JACKET)
        arcade.draw_rectangle_filled(center_x, SCREEN_HEIGHT / 2, LANE_LINE_WIDTH, SCREEN_HEIGHT,
                                     arcade.color.WHITE_SMOKE)

    def update(self, delta_time):
        """ All the logic to move, and the game logic goes here. """
        pass


def main():
    game = MyGame(SCREEN_WIDTH, SCREEN_HEIGHT)
    game.setup()
    arcade.run()


if __name__ == "__main__":
    main()
