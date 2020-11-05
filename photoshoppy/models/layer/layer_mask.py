from __future__ import annotations

import struct
from typing import BinaryIO, List

import photoshoppy
from photoshoppy.utilities.rect import Rect


FLAG_POSITION_RELATIVE = 1 << 0
FLAG_MASK_DISABLED = 1 << 1
FLAG_INVERT_WHEN_BLENDING = 1 << 2
FLAG_MASK_FROM_RENDERING = 1 << 3  # Indicates that the user mask actually came from rendering other data
FLAG_PARAMETERS_APPLIED = 1 << 4  # Indicates that the user mask and/or vector masks have parameters applied to them


class LayerMask:
    def __init__(self, rect: Rect, default_color: int, flags: int):
        self._rect = rect
        self._default_color = default_color
        self._flags = flags
        self._layer = None

    @property
    def rect(self) -> Rect:
        return self._rect

    @property
    def default_color(self) -> int:
        return self._default_color

    @property
    def flags(self) -> int:
        return self._flags

    @property
    def width(self) -> int:
        return self.rect.right - self.rect.left

    @property
    def height(self) -> int:
        return self.rect.bottom - self.rect.top

    @property
    def layer(self) -> photoshoppy.models.layer.model.Layer or None:
        return self._layer

    @layer.setter
    def layer(self, layer: photoshoppy.models.layer.model.Layer):
        self._layer = layer

    def flag_set(self, flag):
        """ Check if a particular flag is set. """
        if self.flags & flag != 0:
            return True
        else:
            return False

    @classmethod
    def from_file(cls, file: BinaryIO, data_length: int) -> LayerMask:
        rect = struct.unpack('>4i', file.read(16))
        rect = Rect(*rect)

        default_color = struct.unpack('>B', file.read(1))[0]
        flags = struct.unpack('>B', file.read(1))[0]

        if flags & FLAG_PARAMETERS_APPLIED != 0:
            pass

        if data_length == 20:
            _ = struct.unpack('>H', file.read(2))  # Padding
        else:
            real_flags = struct.unpack('>B', file.read(1))[0]  # Same as flags information above
            real_user_mask_bg = struct.unpack('>B', file.read(1))[0]
            real_rect = struct.unpack('>4i', file.read(16))
            real_rect = Rect(*real_rect)

        return LayerMask(rect, default_color, flags)
