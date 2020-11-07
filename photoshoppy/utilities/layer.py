from typing import Generator

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


def iter_top_level_layers(psd: PSDFile) -> Generator[Layer, None, None]:
    # Create a temporary "root" layer and parent all top-level Layers to it.
    root = Layer("root")
    root.blend_mode = BlendMode.from_name("pass through")

    for layer in reversed(psd.layers):
        if layer.is_bounding_section_divider:
            continue
        elif layer.parent is None:
            root.add_child(layer)

    for layer in iter_group(root):
        yield layer


def iter_group(group: Layer) -> Generator[Layer, None, None]:
    for layer in group.children:
        yield layer
