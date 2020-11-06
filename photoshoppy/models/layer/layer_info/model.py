from __future__ import annotations

from typing import BinaryIO

from photoshoppy.utilities.read_section import ReadSection


class LayerInfo:
    @classmethod
    def key(cls) -> str:
        raise NotImplementedError

    @classmethod
    def name(cls) -> str:
        raise NotImplementedError

    @classmethod
    def read_section(cls, file: BinaryIO) -> LayerInfo:
        raise NotImplementedError


class TempLayerInfo(LayerInfo):
    """ Temporary class for layer info blocks that haven't yet been implemented.
    Might delete later, idk.
    """
    def __init__(self, key, name, file):
        self._key = key
        self._name = name
        self.read_section(file)

    def key(self) -> str:
        return self._key

    def name(self):
        return self._name

    @classmethod
    def read_section(cls, file: BinaryIO):
        with ReadSection(file):
            pass
