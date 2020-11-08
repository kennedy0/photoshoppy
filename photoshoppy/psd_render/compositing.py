import numpy as np


class IgnoreNumpyErrors:
    """ Context manager to ignore NumPy errors """
    def __init__(self):
        self.old_settings = dict()

    def __enter__(self):
        self.old_settings = np.seterr(all='ignore')
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        np.seterr(**self.old_settings)


def uint8_to_float(data: np.array) -> np.array:
    new_data = data.astype(np.float64)
    new_data /= np.iinfo(np.uint8).max
    return new_data


def float_to_uint8(data: np.array) -> np.array:
    new_data = data * np.iinfo(np.uint8).max
    new_data = np.around(new_data)  # Round before casting to int to avoid errors with floating-point precision
    return new_data.astype(np.uint8)


def premultiply(rgba: np.array) -> np.array:
    rgb = rgba[:, :, :3]
    a = rgba[:, :, 3]
    rgbp = rgb * a[:, :, None]
    return np.dstack([rgbp, a])


def unpremultiply(rgba: np.array) -> np.array:
    rgbp = rgba[:, :, :3]
    a = rgba[:, :, 3]
    rgb = rgbp / a[:, :, None]
    return np.dstack([rgb, a])


def scale_channel(array: np.array, scale: float) -> np.array:
    array = uint8_to_float(array)
    array *= scale
    array = float_to_uint8(array)
    return array


def get_luminosity(rgb: np.array) -> np.array:
    return np.dot(rgb, [0.3, 0.59, 0.11])


def set_luminosity(rgb: np.array, luminosity: np.array) -> np.array:
    d = luminosity - get_luminosity(rgb)
    return clip_color(rgb + d[:, :, None])


def clip_color(rgb: np.array) -> np.array:
    l = get_luminosity(rgb)[:, :, None]
    n = np.min(rgb, axis=2)[:, :, None]
    x = np.max(rgb, axis=2)[:, :, None]

    with IgnoreNumpyErrors():
        color = np.where(n < 0, l + (((rgb - l) * l) / (l - n)),
                         np.where(x > 1, l + (((rgb - l) * (1 - l)) / (x - l)), rgb))

    return color


def get_saturation(rgb: np.array) -> np.array:
    return np.max(rgb, axis=2) - np.min(rgb, axis=2)


def set_saturation(rgb: np.array, saturation: np.array) -> np.array:
    rgb_max = np.max(rgb, axis=2)
    rgb_min = np.min(rgb, axis=2)

    rgb_max = np.dstack([rgb_max, rgb_max, rgb_max])
    rgb_min = np.dstack([rgb_min, rgb_min, rgb_min])
    saturation = np.dstack([saturation, saturation, saturation])

    with IgnoreNumpyErrors():
        color = np.where(rgb_max > rgb_min,
                         np.where(rgb == rgb_max, saturation,
                                  np.where(rgb == rgb_min, 0,
                                           (rgb - rgb_min) * saturation) / (rgb_max - rgb_min)), 0)

    return color


def clamp(array: np.array, minimum: float = 0, maximum: float = 1) -> np.array:
    return np.maximum(minimum, np.minimum(maximum, array))
