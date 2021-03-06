import os

import numpy as np
from PIL import Image

from . import render_utils
from photoshoppy.psd_file import PSDFile
from photoshoppy.utilities.layer import get_root_layer
from photoshoppy.utilities.string import clean_file_name


def render_psd(psd: PSDFile, file_path: str, overwrite: bool = False):
    """ Render the current PSD file. """
    if overwrite is False and os.path.isfile(file_path):
        raise FileExistsError(file_path)

    root = get_root_layer(psd)
    image_data = render_utils.flatten_group(group=root, psd=psd)
    _write_image(image_data, file_path, "RGBA")


def render_layers(psd: PSDFile, folder_path: str, extension: str = "png", overwrite: bool = False,
                  skip_hidden_layers: bool = True, render_masks: bool = False):
    """ Render each layer of a PSD file to a folder. """
    ext = extension.strip(".")
    for layer in psd.iter_layers():
        if layer.visible is False and skip_hidden_layers is True:
            continue

        layer_name = clean_file_name(layer.name)
        layer_path = os.path.join(folder_path, f"{layer_name}.{ext}")
        if overwrite is False and os.path.isfile(layer_path):
            raise FileExistsError(layer_path)

        if len(layer.channels) == 3:
            mode = "RGB"
        else:
            mode = "RGBA"

        _write_image(layer.image_data, layer_path, mode)

        if render_masks:
            if layer.layer_mask is not None:
                mask_path = os.path.join(folder_path, f"{layer_name}_mask.{ext}")
                _write_image(layer.layer_mask.image_data, mask_path, "L")


def render_groups(psd: PSDFile, folder_path: str, extension: str = "png", overwrite: bool = False,
                  skip_hidden_groups: bool = True, render_masks: bool = False):
    """ Render each group of a PSD file to a folder. """
    ext = extension.strip(".")
    for group in psd.iter_groups():
        if group.visible is False and skip_hidden_groups is True:
            continue

        group_name = clean_file_name(group.name)
        group_path = os.path.join(folder_path, f"{group_name}.{ext}")
        if overwrite is False and os.path.isfile(group_path):
            raise FileExistsError(group_path)

        group_image_data = render_utils.composite_group(group=group, psd=psd, bg=None)
        _write_image(group_image_data, group_path, "RGBA")

        if render_masks:
            if group.layer_mask is not None:
                mask_path = os.path.join(folder_path, f"{group_name}_mask.{ext}")
                _write_image(group.layer_mask.image_data, mask_path, "L")


def render_image_data(psd: PSDFile, file_path: str, overwrite: bool = False):
    """ Render the image data from a PSD file as an image.
    This is the flattened representation of the document when it was last saved.
    """
    if overwrite is False and os.path.isfile(file_path):
        raise FileExistsError(file_path)

    mode = _convert_color_mode(psd)
    _write_image(psd.image_data, file_path, mode)


def _write_image(image_data: np.ndarray, file_path, mode: str):
    image = Image.fromarray(image_data, mode=mode)
    image.save(file_path)


def _convert_color_mode(psd: PSDFile) -> str:
    """ Convert Photoshop color mode to PIL mode. """
    ps_to_pil_mode = {
        'Bitmap': "1",
        'Grayscale': "L",
        'Indexed': None,
        'RGB': "RGB",
        'CMYK': "CMYK",
        'Multichannel': None,
        'Duotone': None,
        'Lab': "LAB",
    }
    mode = ps_to_pil_mode[psd.color_mode]
    if mode is None:
        raise NotImplementedError(f"Color mode not supported: {psd.color_mode}")

    if mode == "RGB" and psd.channels == 4:
        mode = "RGBA"

    return mode
