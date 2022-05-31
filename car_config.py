import arcade
import numpy as np
import scipy
from car import CarLanes, Car

def mat_to_numpy(array_path, mat_array_name):

    # load mat array as numpy array
    np_ar = scipy.io.loadmat(array_path + mat_array_name)
    ar = list(np_ar.values())[-1]
    # save numpy array
    np_array_name = (mat_array_name.split('.')[0] + '.npy')
    drop_path = array_path + np_array_name
    np.save(drop_path, ar)
    return ar

COLOR_KEY = "color"
KEYMAP_KEY = "keymap"
vote_path = r'C:\Users\dell\Documents\bci4als\car_game\2cars-fork\\'


CARS_CONFIG = {
    0: {
        COLOR_KEY: arcade.color.DARK_PINK,
        KEYMAP_KEY: {arcade.key.Q: CarLanes.LEFT,
                     arcade.key.E: CarLanes.RIGHT}
    },
    1: {
        COLOR_KEY: arcade.color.REDWOOD,
        KEYMAP_KEY: {arcade.key.I: CarLanes.LEFT,
                     arcade.key.P: CarLanes.RIGHT}
    },
}

# CARS_CONFIG = {
#     0: {
#         COLOR_KEY: arcade.color.TEAL,
#         KEYMAP_KEY: {arcade.key.A: CarLanes.LEFT,
#                      arcade.key.D: CarLanes.RIGHT}
#     },
#     1: {
#         COLOR_KEY: arcade.color.REDWOOD,
#         KEYMAP_KEY: {arcade.key.G: CarLanes.LEFT,
#                      arcade.key.J: CarLanes.RIGHT}
#     },
#     2: {
#         COLOR_KEY: arcade.color.LION,
#         KEYMAP_KEY: {arcade.key.LEFT: CarLanes.LEFT,
#                      arcade.key.RIGHT: CarLanes.RIGHT}
#     },
#     3: {
#         COLOR_KEY: arcade.color.SILVER,
#         KEYMAP_KEY: {arcade.key.NUM_4: CarLanes.LEFT,
#                      arcade.key.NUM_6: CarLanes.RIGHT}
#     }
# }


def get_car(index):
    return Car(CARS_CONFIG[index][COLOR_KEY], CARS_CONFIG[index][KEYMAP_KEY])
