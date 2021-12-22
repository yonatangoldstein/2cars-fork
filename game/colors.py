
def luminance(rgb):
    """
    Calculate the luminance of an RGB color. based on https://stackoverflow.com/a/56678483
    :param rgb: tuple or list of [R,G,B] values from 0 to 255
    :return: a luminance value from 0 to 1 whereas 0 is the darkest, and 1 is the lightest
    """
    # convert to gamma encoding
    vrgb = [c / 255 for c in rgb]
    # convert to linear values
    linear_vrgb = [(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4) for c in vrgb]
    r_lin, g_lin, b_lin = linear_vrgb
    # Apply coefficients
    return r_lin * 0.2126 + g_lin * 0.7152 + b_lin * 0.0722


def adjust_color_to_match_luminance(color, target_luminance, diff_threshold=0.001, max_tries=100000):
    """
    Change RGB color gradually until its luminance matches target
    :param color: list of [R,G,B] values from 0 to 255
    :param target_luminance: the luminance to reach (value from 0 to 1)
    :param diff_threshold: the minimal acceptable difference from target
    :param max_tries: maximum iterations to avoid infinite loop
    :return: the adjusted color
    """
    color_index = 0
    i = 0
    while abs(luminance(color) - target_luminance) > diff_threshold:
        if luminance(color) < target_luminance:
            if color[color_index] < 255:
                color[color_index] += 1
        elif luminance(color) > target_luminance:
            if color[color_index] > 0:
                color[color_index] -= 1
        # rotate color index
        color_index = (color_index + 1) % 3

        if i > max_tries:
            raise Exception("Couldn't match luminance")
        i += 1

    return color
