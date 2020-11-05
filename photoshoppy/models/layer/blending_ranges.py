from __future__ import annotations

import struct
from typing import BinaryIO, List


class BlendRange:
    def __init__(self, data: bytes):
        self.black_low, self.black_high, self.white_low, self.white_high = struct.unpack('>4B', data)


class CSDR:
    """ Channel Source-Destination Range """
    def __init__(self, source: BlendRange, destination: BlendRange):
        self.source = source
        self.destination = destination


class BlendingRanges:
    def __init__(self, gray_range: CSDR, channel_ranges: List[CSDR]):
        self.gray_range = gray_range
        self.channel_ranges = channel_ranges

    @classmethod
    def from_file(cls, file: BinaryIO, section_end: int) -> BlendingRanges:
        gray_blend_src = BlendRange(file.read(4))
        gray_blend_dst = BlendRange(file.read(4))
        gray_range = CSDR(gray_blend_src, gray_blend_dst)

        channel_ranges = []
        while file.tell() < section_end:
            channel_src = BlendRange(file.read(4))
            channel_dst = BlendRange(file.read(4))
            channel_ranges.append(CSDR(channel_src, channel_dst))

        return cls(gray_range, channel_ranges)
