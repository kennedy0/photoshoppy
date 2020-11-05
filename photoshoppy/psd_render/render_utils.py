import numpy as np

from photoshoppy.models.layer.model import Layer
from photoshoppy.psd_file import PSDFile
from photoshoppy.utilities.rect import Rect
from photoshoppy.utilities.array import crop_array, pad_array


def layer_to_screen_space(layer: Layer, psd: PSDFile) -> np.array:
    """ Return a Layer's image data in screen space. """
    bbox = Rect(0, 0, psd.height, psd.width)
    cropped_image_data = crop_array(array=layer.image_data, rect=layer.rect, bbox=bbox)
    ss_image_data = pad_array(array=cropped_image_data, rect=layer.rect, width=psd.width, height=psd.height)
    return ss_image_data


def clamp(n: int, minimum: int, maximum: int) -> int:
    return max(minimum, min(n, maximum))
