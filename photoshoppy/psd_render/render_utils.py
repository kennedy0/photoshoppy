import numpy as np

from photoshoppy.models.blend_mode.model import BlendMode
from photoshoppy.models.layer.model import Layer
from photoshoppy.models.layer.layer_mask import LayerMask
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


def _get_mask(layer: Layer, psd: PSDFile):
    if layer.layer_mask is None:
        return None
    else:
        return mask_to_screen_space(layer, psd)


def composite_group(group: Layer, psd: PSDFile, bg: np.array or None) -> np.array:
    transparent_bg = np.zeros((psd.height, psd.width, 4), dtype=np.uint8)
    if bg is None:
        bg = transparent_bg

    image_data = transparent_bg
    for layer in group.children:
        if layer.visible is False:
            continue

        if layer.is_group is True:
            fg_image_data = composite_group(group=layer, psd=psd, bg=image_data)
        else:
            fg_image_data = layer_to_screen_space(layer, psd)
        image_data = composite_image_data(
            fg=fg_image_data,
            bg=image_data,
            blend_mode=layer.blend_mode,
            mask=_get_mask(layer, psd),
            opacity=layer.opacity)

    return image_data


def flatten_group(group: Layer, psd: PSDFile, pass_through_bg: None or np.array = None) -> np.array:
    transparent_bg = np.zeros((psd.height, psd.width, 4), dtype=np.uint8)
    bg = transparent_bg

    if group.blend_mode.name == "pass through" and pass_through_bg is not None:
        bg = pass_through_bg

    for layer in group.children:
        if layer.visible is False:
            continue

        blend_mode = layer.blend_mode
        if layer.is_group is True:
            fg = flatten_group(group=layer, psd=psd, pass_through_bg=bg)
            if layer.blend_mode.name == "pass through":
                blend_mode = BlendMode.from_name("normal")
        else:
            fg = layer_to_screen_space(layer=layer, psd=psd)

        group_image_data = composite_image_data(
            fg=fg,
            bg=bg,
            blend_mode=blend_mode,
            mask=_get_mask(layer, psd),
            opacity=layer.opacity)

        bg = group_image_data

    image_data = bg

    return image_data



def composite_image_data(fg: np.array, bg: np.array, blend_mode: BlendMode, mask: np.array or None,
                         opacity: float or int) -> np.array:
    if isinstance(opacity, int):
        opacity = opacity / 255.0
    return blend_mode.blend_fn(fg=fg, bg=bg, mask=mask, fg_opacity=opacity)
