import numpy as np

from photoshoppy.models.layer.model import Layer
from photoshoppy.psd_file import PSDFile
from photoshoppy.utilities.rect import Rect


def layer_to_screen_space(layer: Layer, psd: PSDFile) -> np.array:
    """ Return a Layer's image data in screen space. """
    bbox = Rect(0, 0, psd.height, psd.width)
    cropped_data = crop_layer(layer, bbox)

    pad_left = max(0, layer.rect.left)
    pad_right = max(0, bbox.right - layer.rect.right)
    pad_top = max(0, layer.rect.top)
    pad_bottom = max(0, bbox.bottom - layer.rect.bottom)
    pad_x = (pad_left, pad_right)
    pad_y = (pad_top, pad_bottom)

    ss_image_data = np.pad(cropped_data, pad_width=(pad_y, pad_x, (0, 0)), mode='constant', constant_values=0)

    return ss_image_data


def crop_layer(layer: Layer, bbox: Rect) -> np.array:
    """ Return a layer's image data cropped to a bounding box. """
    left = clamp(bbox.left - layer.rect.left, minimum=0, maximum=layer.width)
    right = clamp(bbox.right - layer.rect.left, minimum=0, maximum=layer.width)
    top = clamp(bbox.top - layer.rect.top, minimum=0, maximum=layer.height)
    bottom = clamp(bbox.bottom - layer.rect.top, minimum=0, maximum=layer.height)
    return layer.image_data[top:bottom, left:right, :]


def clamp(n: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(n, maximum))
