from __future__ import annotations

import os
import struct
from typing import BinaryIO, List

import numpy as np

from .layer_channel import LayerChannel
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
    def __init__(self, name: str, rect: Rect = Rect(0, 0, 0, 0), channels: List[LayerChannel] = None,
                 blend: BlendMode = BlendMode.from_name("normal"), opacity: int = 255, clipping_base: bool = True,
                 flags: int = FLAG_HAS_USEFUL_INFORMATION):
        self._name = name
        self._rect = rect
        if channels is None:
            channels = []
        self._channels = channels
        self._blend_mode = blend
        self._opacity = opacity
        self._clipping_base = clipping_base
        self._flags = flags
        self._image_data = np.empty(0)

        self._blending_ranges = None
        self._layer_mask = None

    @property
    def name(self) -> str:
        return self._name

    @property
    def rect(self) -> Rect:
        return self._rect

    @property
    def width(self) -> int:
        return self.rect.right - self.rect.left
    
    @property
    def height(self) -> int:
        return self.rect.bottom - self.rect.top

    @property
    def channels(self) -> List[LayerChannel]:
        return self._channels

    @property
    def blend_mode(self) -> BlendMode:
        return self._blend_mode

    @property
    def opacity(self) -> int:
        # 0 = Transparent; 255 = Opaque
        return self._opacity

    @property
    def clipping_base(self) -> bool:
        return self._clipping_base

    @property
    def transparency_protected(self) -> bool:
        return self.flag_set(FLAG_TRANSPARANCY_PROTECTED)

    @property
    def visible(self) -> bool:
        if self.flag_set(FLAG_VISIBLE):
            # When the visibility flag is set, it indicates that the layer is NOT visible. Seems backwards...
            return False
        else:
            return True

    @property
    def pixel_data_irrelevant(self) -> bool:
        # If True, pixel data is irrelevant to the appearance of the document
        use_bit_4 = self.flag_set(FLAG_HAS_USEFUL_INFORMATION)
        if use_bit_4 and self.flag_set(FLAG_PIXEL_DATA_IRRELEVANT_TO_APPEARANCE_IN_DOCUMENT):
            return True
        else:
            return False

    @property
    def image_data(self):
        """ Returns the Layer's image data as a composited RGBA image. """
        r = self.get_channel("red")
        g = self.get_channel("green")
        b = self.get_channel("blue")
        a = self.get_channel("transparency mask")

        # Get alpha channel
        if a is None:
            # If no alpha channel is present, generate one with the layer's opacity value
            alpha = np.full((self.height, self.width), 255, dtype=np.uint8)
        else:
            # Return the alpha channel, scaled by the opacity value
            alpha = a.channel_data

        # Layer fill scales the overall opacity
        # ToDo: Get layer fill value
        fill = 1.0
        alpha = scale_channel(alpha, fill)

        image_data = np.dstack([r.channel_data, g.channel_data, b.channel_data, alpha])
        return image_data

    @property
    def blending_ranges(self):
        return self._blending_ranges

    @blending_ranges.setter
    def blending_ranges(self, blending_ranges: BlendingRanges):
        self._blending_ranges = blending_ranges

    @property
    def layer_mask(self):
        return self._layer_mask

    @layer_mask.setter
    def layer_mask(self, layer_mask: LayerMask):
        self._layer_mask = layer_mask

    def get_channel(self, name) -> LayerChannel or None:
        for channel in self.channels:
            if channel.name == name:
                return channel
        return None

    def flag_set(self, flag):
        """ Check if a particular flag is set. """
        if self._flags & flag != 0:
            return True
        else:
            return False

    @classmethod
    def read_layer_record(cls, file: BinaryIO) -> Layer:
        """ Create a new Layer by reading its Layer Record from a file. """
        rect = struct.unpack('>4i', file.read(16))  # (Top, Left, Bottom, Right)
        rect = Rect(*rect)

        channels = []
        num_channels = struct.unpack('>H', file.read(2))[0]
        for channel in range(num_channels):
            channel_id = struct.unpack('>h', file.read(2))[0]
            channel_data_length = struct.unpack('>L', file.read(4))[0]
            channels.append(LayerChannel(channel_id))

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

        layer = Layer(name, rect, channels, blend, opacity, clipping_base, flags)
        layer.blending_ranges = blending_ranges
        if layer_mask is not None:
            layer.layer_mask = layer_mask
        return layer
