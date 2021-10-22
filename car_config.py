import arcade
from car import CarLanes, Car

COLOR_KEY = "color"
KEYMAP_KEY = "keymap"


CARS_CONFIG = {
    0: {
        COLOR_KEY: arcade.color.TEAL,
        KEYMAP_KEY: {arcade.key.A: CarLanes.LEFT,
                     arcade.key.D: CarLanes.RIGHT}
    },
    1: {
        COLOR_KEY: arcade.color.REDWOOD,
        KEYMAP_KEY: {arcade.key.G: CarLanes.LEFT,
                     arcade.key.J: CarLanes.RIGHT}
    },
    2: {
        COLOR_KEY: arcade.color.LION,
        KEYMAP_KEY: {arcade.key.LEFT: CarLanes.LEFT,
                     arcade.key.RIGHT: CarLanes.RIGHT}
    },
    3: {
        COLOR_KEY: arcade.color.SILVER,
        KEYMAP_KEY: {arcade.key.NUM_4: CarLanes.LEFT,
                     arcade.key.NUM_6: CarLanes.RIGHT}
    }
}


def get_car(index):
    return Car(CARS_CONFIG[index][COLOR_KEY], CARS_CONFIG[index][KEYMAP_KEY])
