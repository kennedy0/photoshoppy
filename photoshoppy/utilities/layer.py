import copy

from photoshoppy.models.blend_mode.model import BlendMode
from photoshoppy.models.layer.model import Layer
from photoshoppy.psd_file import PSDFile


def get_root_layer(psd: PSDFile) -> Layer:
    """ Create a "root" layer with a copy of all top-level Layers parented to it. """
    root = Layer("root")

    for _layer in reversed(psd.layers):
        layer = copy.deepcopy(_layer)
        if layer.is_bounding_section_divider:
            continue
        elif layer.parent is None:
            root.add_child(layer)

    return root
