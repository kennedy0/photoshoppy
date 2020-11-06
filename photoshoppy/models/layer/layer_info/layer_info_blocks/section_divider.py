from __future__ import annotations

import enum
import struct
from typing import BinaryIO

from photoshoppy.models.layer.layer_info.model import LayerInfo
from photoshoppy.models.blend_mode.model import BlendMode
from photoshoppy.utilities.read_section import ReadSection
from photoshoppy.utilities.string import unpack_string


class DividerType(enum.Enum):
    Other = 0
    OpenFolder = 1
    ClosedFolder = 2
    BoundingSectionDivider = 3


class SubType(enum.Enum):
    Normal = 0
    SceneGroup = 1  # Affects the animation timeline


class SectionDivider(LayerInfo):
    def __init__(self, divider_type: DividerType, blend_mode: BlendMode, sub_type: SubType):
        self._divider_type = divider_type
        self._blend_mode = blend_mode
        self._sub_type = sub_type

    @property
    def divider_type(self) -> DividerType:
        return self._divider_type

    @property
    def blend_mode(self) -> BlendMode:
        return self._blend_mode

    @property
    def sub_type(self) -> SubType:
        return self._sub_type

    @classmethod
    def key(cls) -> str:
        return "lsct"

    @classmethod
    def name(cls) -> str:
        return "Section Divider"

    @classmethod
    def read_section(cls, file: BinaryIO) -> SectionDivider:
        with ReadSection(file) as section:
            divider_value = struct.unpack('>I', file.read(4))[0]
            divider = DividerType(divider_value)
            blend_mode = BlendMode.from_name("normal")
            sub_type = SubType(0)

            if section.section_length >= 12:
                unpack_string(file.read(4), length=4)  # Signature = 8BIM
                blend_mode_key = unpack_string(file.read(4), length=4)  # Signature = 8BIM
                blend_mode = BlendMode.from_key(blend_mode_key)

                if section.section_length >= 16:
                    sub_type_value = struct.unpack('>I', file.read(4))[0]
                    sub_type = SubType(sub_type_value)

        return cls(divider, blend_mode, sub_type)
