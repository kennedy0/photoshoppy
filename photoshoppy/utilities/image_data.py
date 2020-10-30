import struct
from typing import BinaryIO, List

import numpy as np

from .packbits import unpack_bits


COMPRESSION_RAW = 0
COMPRESSION_RLE = 1
COMPRESSION_ZIP_WITHOUT_PREDICTION = 2
COMPRESSION_ZIP_PREDICTION = 3


def get_image_data(file: BinaryIO, compression: int, width: int, height: int, channels: int, depth: int = 8) -> np.ndarray:
    """ Read image data from a chunk of bytes. Returns a numpy array."""
    # Convert photoshop color depth to c type
    ps_to_c_depth = {1: "B", 8: "B", 16: "H", 32: "I"}
    c_data_type = ps_to_c_depth[depth]

    # Convert photoshop color depth to numpy data type
    ps_to_np_depth = {1: np.bool_, 8: np.uint8, 16: np.uint16, 32: np.uint32}
    np_data_type = ps_to_np_depth[depth]

    # Initialize empty array
    image_data = np.zeros((height, width, channels), dtype=np_data_type)

    if compression == COMPRESSION_RAW:
        scanlines = _read_raw(file=file, width=width, height=height, channels=channels, data_format=c_data_type)
    elif compression == COMPRESSION_RLE:
        scanlines = _read_rle(file=file, width=width, height=height, channels=channels, data_format=c_data_type)
    elif compression == COMPRESSION_ZIP_WITHOUT_PREDICTION:
        raise NotImplementedError("Unsupported compression method: ZIP without prediction")
    elif compression == COMPRESSION_ZIP_PREDICTION:
        raise NotImplementedError("Unsupported compression method: ZIP with prediction")
    else:
        raise NotImplementedError(f"Unknown compression method: {compression}")

    # Write scanlines into image data
    row = 0
    channel = 0
    for i, scanline in enumerate(scanlines):
        if row >= height:
            row -= height
            channel += 1
        image_data[row, :, channel] = scanline
        row += 1

    return image_data


def _read_raw(file: BinaryIO, width: int, height: int, channels: int, data_format: str) -> List[int or float]:
    """ Raw image data. """
    scanlines = []
    for channel in range(channels):
        for row in range(height):
            data = file.read(width)
            scanline = struct.unpack(f'>{width}{data_format}', data)
            scanlines.append(scanline)
    return scanlines


def _read_rle(file: BinaryIO, width: int, height: int, channels: int, data_format: str) -> List[int or float]:
    """ RLE data is stored with the PackBits compression scheme. """
    # First part of RLE image data stores the lengths of each data segment
    data_lengths = []
    for channel in range(channels):
        for row in range(height):
            length = struct.unpack('>H', file.read(2))[0]
            data_lengths.append(length)

    # Decompress each scanline
    scanlines = []
    for length in data_lengths:
        data = unpack_bits(file.read(length))
        scanline = struct.unpack(f'>{width}{data_format}', data)
        scanlines.append(scanline)

    return scanlines
