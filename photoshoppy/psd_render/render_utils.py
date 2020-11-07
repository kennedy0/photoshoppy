import numpy as np

from photoshoppy.models.blend_mode.model import BlendMode
from photoshoppy.models.layer.model import Layer
from photoshoppy.psd_file import PSDFile
from photoshoppy.utilities.rect import Rect
from photoshoppy.utilities.array import crop_array, pad_array


def layer_to_screen_space(layer: Layer, psd: PSDFile) -> np.array:
    """ Return a Layer's image data in screen space. """
    return _image_to_screen_space(
        image_data=layer.image_data,
        image_rect=layer.rect,
        width=psd.width,
        height=psd.height,
        fill=0)


def mask_to_screen_space(layer: Layer, psd: PSDFile) -> np.array:
    """ Return a Layer's mask in screen space. """
    if layer.layer_mask is None:
        raise RuntimeError(f"Layer '{layer.name}' has no layer mask; cannot convert to screen space.")
    return _image_to_screen_space(
        image_data=layer.layer_mask.image_data,
        image_rect=layer.layer_mask.rect,
        width=psd.width,
        height=psd.height,
        fill=layer.layer_mask.default_color)


def _image_to_screen_space(image_data: np.array, image_rect: Rect, width: int, height: int, fill: int = 0) -> np.array:
    bbox = Rect(0, 0, height, width)
    cropped_image_data = crop_array(array=image_data, rect=image_rect, bbox=bbox)
    ss_image_data = pad_array(array=cropped_image_data, rect=image_rect, width=width, height=height, fill_value=fill)
    return ss_image_data


def get_group_image_data(group: Layer, psd: PSDFile) -> np.array:
    """ 'Flatten' a group into a single image. """
    transparent = np.zeros((psd.height, psd.width, 4), dtype=np.uint8)
    image_data = transparent
    for layer in group.children:
        if layer.visible is False:
            # Skip invisible layers
            continue

        # Get image data for layer
        if layer.is_group:
            # Recursive call for groups
            layer_image_data = get_group_image_data(layer, psd)
            layer_rect = Rect(0, 0, psd.height, psd.width)
        else:
            layer_image_data = layer.image_data
            layer_rect = layer.rect

        # Transform layer data to screen space (clipping data outside document size)
        ss_image_data = _image_to_screen_space(
            image_data=layer_image_data,
            image_rect=layer_rect,
            width=psd.width,
            height=psd.height)
        layer_opacity = layer.opacity / 255.0  # Foreground opacity as a floating point value

        # Get layer mask
        if layer.layer_mask is not None:
            mask = mask_to_screen_space(layer, psd)
        else:
            mask = None

        # Composite layer data on top of image data
        image_data = layer.blend_mode.blend_fn(
            fg=ss_image_data,
            bg=image_data,
            mask=mask,
            fg_opacity=layer_opacity)

    # Composite result on top of transparent image (to apply masking and transparency)
    if group.layer_mask is not None:
        group_mask = mask_to_screen_space(group, psd)
    else:
        group_mask = None
    group_opacity = group.opacity / 255.0

    blend_normal_fn = BlendMode.from_name("normal").blend_fn
    group_image_data = blend_normal_fn(
        fg=image_data,
        bg=transparent,
        mask=group_mask,
        fg_opacity=group_opacity)

    return group_image_data
