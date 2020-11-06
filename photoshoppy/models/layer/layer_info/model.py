from __future__ import annotations

import struct
from typing import BinaryIO

from .constants import layer_info_names
from photoshoppy.models.blend_mode.model import BlendMode
from photoshoppy.utilities.string import unpack_string
from photoshoppy.utilities.read_section import ReadSection


def read_layer_info(file: BinaryIO) -> LayerInfo:
    unpack_string(file.read(4), length=4)  # Signature: 8BIM or 8B64
    layer_info_key = unpack_string(file.read(4), length=4)
    layer_info_class = layer_info_dispatch.get(layer_info_key)  # type: LayerInfo
    if layer_info_class is None:
        layer_info = None
        with ReadSection(file):
            pass
    else:
        layer_info = layer_info_class.read_layer_info(file)
    return layer_info


class LayerInfo:
    @classmethod
    def key(cls) -> str:
        raise NotImplementedError

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def read_layer_info(cls, file: BinaryIO):
        raise NotImplementedError


class SectionDivider(LayerInfo):
    def __init__(self, divider_type: int, blend_mode: BlendMode = None, sub_type: int = None):
        if blend_mode is None:
            blend_mode = BlendMode.from_name("normal")
        if sub_type is None:
            sub_type = 0
        self._divider_type = divider_type
        self._blend_mode = blend_mode
        self._sub_type = sub_type

    @property
    def divider_type(self) -> int:
        return self._divider_type

    @property
    def blend_mode(self) -> BlendMode:
        return self._blend_mode

    @property
    def sub_type(self) -> int:
        return self._sub_type

    @classmethod
    def key(cls) -> str:
        return "lsct"

    @classmethod
    def name(cls) -> str:
        return "Section Divider"

    @classmethod
    def read_layer_info(cls, file: BinaryIO) -> SectionDivider:
        with ReadSection(file) as section:
            divider_type = struct.unpack('>I', file.read(4))[0]
            blend_mode = None
            sub_type = None
            if section.section_length >= 12:
                unpack_string(file.read(4), length=4)  # Signature = 8BIM
                blend_mode_key = unpack_string(file.read(4), length=4)  # Signature = 8BIM
                blend_mode = BlendMode.from_key(blend_mode_key)
                if section.section_length >= 16:
                    sub_type = struct.unpack('>I', file.read(4))[0]
        return cls(divider_type, blend_mode, sub_type)


layer_info_dispatch = {
    'lsct': SectionDivider
}
