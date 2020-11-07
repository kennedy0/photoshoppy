from __future__ import annotations

import os
import struct
from typing import BinaryIO, Generator, List

import numpy as np

from .layer_channel import LayerChannel
from .layer_channel import CHANNEL_RED, CHANNEL_GREEN, CHANNEL_BLUE
from .layer_channel import CHANNEL_TRANSPARENCY_MASK
from .layer_info.model import LayerInfo
from .layer_info.layer_info_blocks.section_divider import SectionDivider, DividerType
from .layer_info.utilities import read_layer_info
from .layer_mask import LayerMask
from .blending_ranges import BlendingRanges
from photoshoppy.models.blend_mode.model import BlendMode
from photoshoppy.psd_render.compositing import scale_channel
from photoshoppy.utilities.read_section import ReadSection
from photoshoppy.utilities.rect import Rect
from photoshoppy.utilities.string import unpack_string, read_pascal_string


FLAG_TRANSPARANCY_PROTECTED = 1 << 0
FLAG_VISIBLE = 1 << 1
FLAG_OBSOLETE = 1 << 2
FLAG_HAS_USEFUL_INFORMATION = 1 << 3
FLAG_PIXEL_DATA_IRRELEVANT_TO_APPEARANCE_IN_DOCUMENT = 1 << 4
FLAG_UNDOCUMENTED = 1 << 5


class Layer:
    def __init__(self, name: str):
        self._name = name
        self._rect = Rect(0, 0, 0, 0)
        self._channels = []
        self._blend_mode = BlendMode.from_name("normal")
        self._opacity = 255
        self._clipping_base = True
        self._flags = FLAG_HAS_USEFUL_INFORMATION
        self._image_data = np.empty(0)

        self._blending_ranges = None
        self._layer_mask = None
        self._layer_info = []

        self._is_group = False
        self._is_bounding_section_divider = False
        self._parent = None
        self._children = []

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, name: str):
        self._name = name

    @property
    def rect(self) -> Rect:
        return self._rect

    @rect.setter
    def rect(self, rect: Rect):
        self._rect = rect

    @property
    def width(self) -> int:
        return self.rect.right - self.rect.left
    
    @property
    def height(self) -> int:
        return self.rect.bottom - self.rect.top

    @property
    def channels(self) -> List[LayerChannel]:
        return self._channels

    def add_channel(self, channel_id: int):
        self._channels.append(LayerChannel(channel_id=channel_id, layer=self))

    def get_channel(self, name: str) -> LayerChannel or None:
        for channel in self.channels:
            if channel.name == name:
                return channel
        return None

    @property
    def blend_mode(self) -> BlendMode:
        return self._blend_mode

    @blend_mode.setter
    def blend_mode(self, blend_mode: BlendMode):
        self._blend_mode = blend_mode

    @property
    def opacity(self) -> int:
        # 0 = Transparent; 255 = Opaque
        return self._opacity

    @opacity.setter
    def opacity(self, opacity: int or float):
        if type(opacity) == int:
            self._opacity = opacity
        elif type(opacity) == float:
            self._opacity = int(opacity * 255)
        else:
            raise TypeError("opacity must be int or float")

    @property
    def clipping_base(self) -> bool:
        return self._clipping_base

    @clipping_base.setter
    def clipping_base(self, clipping_base: bool):
        self._clipping_base = clipping_base

    @property
    def flags(self) -> int:
        return self._flags

    @flags.setter
    def flags(self, flags: int):
        self._flags = flags

    def flag_is_set(self, flag: int) -> bool:
        """ Check if a particular flag is set. """
        if self._flags & flag != 0:
            return True
        else:
            return False

    @property
    def transparency_protected(self) -> bool:
        return self.flag_is_set(FLAG_TRANSPARANCY_PROTECTED)

    @property
    def visible(self) -> bool:
        if self.flag_is_set(FLAG_VISIBLE):
            # When the visibility flag is set, it indicates that the layer is NOT visible. Seems backwards...
            return False
        else:
            return True

    @visible.setter
    def visible(self, visible: bool):
        if visible is True:
            self._flags = self._flags | FLAG_VISIBLE
        else:
            self._flags = self._flags & ~FLAG_VISIBLE

    @property
    def pixel_data_irrelevant(self) -> bool:
        # If True, pixel data is irrelevant to the appearance of the document
        use_bit_4 = self.flag_is_set(FLAG_HAS_USEFUL_INFORMATION)
        if use_bit_4 and self.flag_is_set(FLAG_PIXEL_DATA_IRRELEVANT_TO_APPEARANCE_IN_DOCUMENT):
            return True
        else:
            return False

    @property
    def image_data(self):
        """ Returns the Layer's image data as a composited RGBA image. """
        r = self.get_channel(CHANNEL_RED)
        g = self.get_channel(CHANNEL_GREEN)
        b = self.get_channel(CHANNEL_BLUE)
        a = self.get_channel(CHANNEL_TRANSPARENCY_MASK)

        # Get alpha channel.
        if a is None:
            # If no alpha channel is present, generate one with the layer's opacity value
            alpha = np.full((self.height, self.width), 255, dtype=np.uint8)
        else:
            # Return the alpha channel
            alpha = a.channel_data

        # Layer fill scales the overall opacity
        # ToDo: Get layer fill value
        fill = 1.0
        alpha = scale_channel(alpha, fill)

        image_data = np.dstack([r.channel_data, g.channel_data, b.channel_data, alpha])
        return image_data

    @property
    def blending_ranges(self) -> BlendingRanges:
        return self._blending_ranges

    @blending_ranges.setter
    def blending_ranges(self, blending_ranges: BlendingRanges):
        self._blending_ranges = blending_ranges

    @property
    def layer_mask(self) -> LayerMask:
        return self._layer_mask

    @layer_mask.setter
    def layer_mask(self, layer_mask: LayerMask):
        layer_mask.layer = self
        self._layer_mask = layer_mask

    @property
    def layer_info(self) -> List[LayerInfo]:
        return self._layer_info

    def add_layer_info(self, layer_info: LayerInfo):
        self._layer_info.append(layer_info)
        if isinstance(layer_info, SectionDivider):
            if layer_info.divider_type in [DividerType.OpenFolder, DividerType.ClosedFolder]:
                self._is_group = True
            elif layer_info.divider_type == DividerType.BoundingSectionDivider:
                self._is_bounding_section_divider = True

    @property
    def is_group(self) -> bool:
        return self._is_group

    @property
    def is_bounding_section_divider(self) -> bool:
        return self._is_bounding_section_divider

    @property
    def parent(self) -> Layer or None:
        return self._parent

    @parent.setter
    def parent(self, parent: Layer or None):
        self._parent = parent
        if isinstance(parent, Layer):
            parent.add_child(self)

    @property
    def children(self) -> List[Layer]:
        return self._children

    def add_child(self, child: Layer):
        self._children.insert(0, child)

    @classmethod
    def read_layer_record(cls, file: BinaryIO) -> Layer:
        """ Create a new Layer by reading its Layer Record from a file. """
        rect = struct.unpack('>4i', file.read(16))  # (Top, Left, Bottom, Right)
        rect = Rect(*rect)

        channel_ids = []
        num_channels = struct.unpack('>H', file.read(2))[0]
        for channel in range(num_channels):
            channel_id = struct.unpack('>h', file.read(2))[0]
            channel_data_length = struct.unpack('>L', file.read(4))[0]
            channel_ids.append(channel_id)

        unpack_string(file.read(4), length=4)  # Blend mode signature = 8BIM
        blend_mode_key = unpack_string(file.read(4), length=4)
        blend = BlendMode.from_key(blend_mode_key)

        opacity = struct.unpack('>B', file.read(1))[0]

        clipping = struct.unpack('>B', file.read(1))[0]
        if clipping == 0:
            clipping_base = True
        else:
            clipping_base = False

        flags = struct.unpack('>B', file.read(1))[0]

        file.seek(1, os.SEEK_CUR)  # Filler byte

        with ReadSection(file) as extra_data_section:
            with ReadSection(file) as layer_mask_section:
                if layer_mask_section.section_length > 0:
                    layer_mask = LayerMask.from_file(file, data_length=layer_mask_section.section_length)
                else:
                    layer_mask = None
            with ReadSection(file) as blending_ranges_section:
                blending_ranges = BlendingRanges.from_file(file, section_end=blending_ranges_section.section_end)

            # Layer name (Pascal string padded to 4 bytes)
            layer_name_pstring = read_pascal_string(file, padding=4)
            name = layer_name_pstring.value

            # Read additional layer info
            layer_info_list = []
            while file.tell() < extra_data_section.section_end:
                layer_info = read_layer_info(file)
                layer_info_list.append(layer_info)

        # Build Layer
        layer = Layer(name)
        layer.rect = rect
        layer.blend_mode = blend
        layer.opacity = opacity
        layer.clipping_base = clipping_base
        layer.flags = flags

        for channel_id in channel_ids:
            layer.add_channel(channel_id)
        layer.blending_ranges = blending_ranges

        if layer_mask is not None:
            layer.layer_mask = layer_mask

        for layer_info in layer_info_list:
            layer.add_layer_info(layer_info)

        return layer
