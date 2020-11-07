import os
import struct
import sys
from typing import List, Generator

import numpy as np

from .utilities.image_data import get_image_data
from .utilities.read_section import ReadSection
from .models.image_resource.model import ImageResourceBlock
from .models.layer.model import Layer
from .models.errors import PSDReadError


class PSDFile:
    def __init__(self, file_path):
        self._file_path = file_path
        self._channels = None
        self._width = None
        self._height = None
        self._depth = None
        self._color_mode = None

        self._image_resources = []
        self._layers = []

        self._image_data = np.empty(0)

        self._file = None
        self._read_file()
        self._organize_layers()

    @property
    def file_path(self) -> str:
        return self._file_path

    @property
    def channels(self) -> int:
        return self._channels

    @property
    def width(self) -> int:
        return self._width

    @property
    def height(self) -> int:
        return self._height

    @property
    def depth(self) -> int:
        return self._depth

    @property
    def color_mode(self) -> str:
        return self._color_mode

    @property
    def image_resources(self) -> List[ImageResourceBlock]:
        return self._image_resources

    @property
    def layers(self) -> List[Layer]:
        return self._layers

    @property
    def image_data(self) -> np.ndarray:
        return self._image_data

    def print_file_info(self):
        """ Print summary information about this file. """
        print(f"path: {self.file_path}")
        print(f"resolution: {self.width}x{self.height}")
        print(f"channels: {self.channels}")
        print(f"bits per channel: {self.depth}")
        print(f"color mode: {self.color_mode}")

    def layer(self, layer_name) -> Layer:
        """ Retrieve a layer by name. """
        for layer in self.layers:
            if layer.name == layer_name:
                return layer
        raise RuntimeError(f"Layer '{layer_name}' not found")

    def _offset(self) -> int:
        """ Returns the current offset. """
        if self._file is not None:
            return self._file.tell()
        else:
            return -1

    def _read_file(self):
        with open(self.file_path, 'rb') as f:
            self._file = f
            self._read_file_header()
            self._read_color_mode_data()
            self._read_image_resources()
            self._read_layer_and_mask_information()
            self._read_image_data()

    def _read_file_header(self):
        signature = struct.unpack(f'>4s', self._file.read(4))[0]
        if signature != b"\x38\x42\x50\x53":  # 8BPS
            raise PSDReadError(f"Invalid signature: \'{signature}\'. File is not a Photoshop file: {self.file_path}")

        version = struct.unpack('>H', self._file.read(2))[0]
        if version == 2:
            raise PSDReadError(f"PSB file format is not supported.")

        self._file.seek(6, os.SEEK_CUR)  # Reserved bytes

        self._channels = struct.unpack('>H', self._file.read(2))[0]
        self._height, self._width = struct.unpack('>2L', self._file.read(8))
        self._depth = struct.unpack('>H', self._file.read(2))[0]

        color_mode = struct.unpack('>H', self._file.read(2))[0]
        color_modes = {
            0: "Bitmap",
            1: "Grayscale",
            2: "Indexed",
            3: "RGB",
            4: "CMYK",
            7: "Multichannel",
            8: "Duotone",
            9: "Lab",
        }
        self._color_mode = color_modes[color_mode]

    def _read_color_mode_data(self):
        """ Only indexed and duotone color have this data. For all other modes, this is just the 4-byte length field,
        which is set to zero.
        """
        with ReadSection(self._file):
            pass

    def _read_image_resources(self):
        """ Image Resources store non-pixel data associated with images, such as pen tool paths. """
        with ReadSection(self._file) as section:
            while self._offset() < section.section_end:
                block = ImageResourceBlock(self._file)
                self._image_resources.append(block)

    def _read_layer_and_mask_information(self):
        """ Information about layers and masks. """
        with ReadSection(self._file) as section:
            if section.section_length > 0:  # If no layers are present, section length is zero
                self._read_layer_info()
                self._read_global_layer_mask_info()
                self._read_additional_layer_info()

    def _read_layer_info(self):
        with ReadSection(self._file):
            layer_count = struct.unpack('>h', self._file.read(2))[0]
            if layer_count < 0:
                # If layer count is negative, its absolute value is the number of layers, and the first alpha channel
                #   contains the transparency data for the merged result.
                layer_count = abs(layer_count)

            # Create layers from layer records
            for i in range(layer_count):
                layer = Layer.read_layer_record(self._file)
                self._layers.append(layer)

            # Read layer channel data
            for layer in self.layers:
                for channel in layer.channels:
                    channel.read_channel_data(file=self._file)

    def _read_global_layer_mask_info(self):
        with ReadSection(self._file):
            pass

    def _read_additional_layer_info(self):
        pass

    def _read_image_data(self):
        """ Image pixel data. This is the complete merged/composited image. """
        compression_method = struct.unpack('>H', self._file.read(2))[0]
        self._image_data = get_image_data(
            file=self._file,
            compression=compression_method,
            width=self.width,
            height=self.height,
            channels=self.channels,
            depth=self.depth)

    def _organize_layers(self):
        """ Assign layer parents. """
        parent = None
        for layer in reversed(self.layers):
            if layer.is_group:
                layer.parent = parent
                parent = layer
            elif layer.is_bounding_section_divider:
                parent = parent.parent
            else:
                layer.parent = parent

    def iter_layers(self) -> Generator[Layer, None, None]:
        for layer in self.layers:
            if layer.is_group or layer.is_bounding_section_divider:
                continue
            else:
                yield layer

    def iter_groups(self) -> Generator[Layer, None, None]:
        for layer in self.layers:
            if layer.is_group:
                yield layer


if __name__ == "__main__":
    paths = sys.argv[1:]
    for p in paths:
        print(f"reading {p}")
        psd = PSDFile(p)
        psd.print_file_info()
