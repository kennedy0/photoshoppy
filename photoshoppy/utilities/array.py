import numpy as np

from .rect import Rect


def crop_array(array: np.array, rect: Rect, bbox: Rect) -> np.array:
    """ Return a layer's image data cropped to a bounding box. """
    width = bbox.right - bbox.left
    height = bbox.bottom - bbox.top

    left = clamp(bbox.left - rect.left, minimum=0, maximum=width)
    right = clamp(bbox.right - rect.left, minimum=0, maximum=width)
    top = clamp(bbox.top - rect.top, minimum=0, maximum=height)
    bottom = clamp(bbox.bottom - rect.top, minimum=0, maximum=height)

    if array.ndim == 2:
        return array[top:bottom, left:right]
    else:
        return array[top:bottom, left:right, :]


def pad_array(array: np.array, rect: Rect, width: int, height: int, fill_value: int = 0):
    bbox = Rect(0, 0, height, width)

    pad_left = max(0, rect.left)
    pad_right = max(0, bbox.right - rect.right)
    pad_top = max(0, rect.top)
    pad_bottom = max(0, bbox.bottom - rect.bottom)

    pad_x = (pad_left, pad_right)
    pad_y = (pad_top, pad_bottom)

    if array.ndim == 2:
        return np.pad(array, pad_width=(pad_y, pad_x), mode='constant', constant_values=fill_value)
    else:
        return np.pad(array, pad_width=(pad_y, pad_x, (0, 0)), mode='constant', constant_values=fill_value)


def clamp(n: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(n, maximum))
