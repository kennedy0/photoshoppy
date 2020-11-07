import copy

from photoshoppy.models.blend_mode.model import BlendMode
from photoshoppy.models.layer.model import Layer
from photoshoppy.psd_file import PSDFile


def get_render_visibility(layer: Layer) -> bool:
    """ Traverse this Layer's parents to determine render visibility.
    If any of this Layer's parents are not visible, the Layer is not visible.
    """
    parent: Layer = layer.parent
    while parent is not None:
        if parent.visible is False:
            return False
        else:
            parent: Layer or None = parent.parent
    return layer.visible


def get_root_layer(psd: PSDFile) -> Layer:
    """ Create a temporary "root" layer and parent all top-level Layers to it. """
    root = Layer("root")
    root.blend_mode = BlendMode.from_name("pass through")

    for _layer in reversed(psd.layers):
        layer = copy.deepcopy(_layer)
        if layer.is_bounding_section_divider:
            continue
        elif layer.parent is None:
            root.add_child(layer)

    return root
