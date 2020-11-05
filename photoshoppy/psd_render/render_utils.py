import numpy as np

from photoshoppy.models.layer.model import Layer
from photoshoppy.psd_file import PSDFile
from photoshoppy.utilities.rect import Rect
from photoshoppy.utilities.array import crop_array, pad_array


def layer_to_screen_space(layer: Layer, psd: PSDFile) -> np.array:
    """ Return a Layer's image data in screen space. """
    return _image_to_screen_space(layer.image_data, layer.rect, psd.width, psd.height)


def mask_to_screen_space(layer: Layer, psd: PSDFile) -> np.array:
    """ Return a Layer's mask in screen space. """
    if layer.layer_mask is None:
        raise RuntimeError(f"Layer '{layer.name}' has no layer mask; cannot convert to screen space.")
    return _image_to_screen_space(layer.layer_mask.image_data, layer.layer_mask.rect, psd.width, psd.height)


def _image_to_screen_space(image_data: np.array, image_rect: Rect, width: int, height: int) -> np.array:
    bbox = Rect(0, 0, height, width)
    cropped_image_data = crop_array(array=image_data, rect=image_rect, bbox=bbox)
    ss_image_data = pad_array(array=cropped_image_data, rect=image_rect, width=width, height=height)
    return ss_image_data
