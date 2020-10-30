import os
import struct
from typing import BinaryIO


class ReadSection:
    """ Context manager for reading a PSD section. Upon finishing, it moves the current position offset to the end of
    the section.
    """
    def __init__(self, file: BinaryIO):
        self.file = file
        self.section_start = file.tell()
        self.section_end = None
        self.section_length = None

    def __enter__(self):
        self.go_to_section_start()
        self.section_length = struct.unpack('>L', self.file.read(4))[0]
        self.section_end = self.file.tell() + self.section_length
        self.go_to_section_data()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.go_to_section_end()

    def go_to_section_start(self):
        self.file.seek(self.section_start, os.SEEK_SET)

    def go_to_section_end(self):
        self.file.seek(self.section_end, os.SEEK_SET)

    def go_to_section_data(self):
        """ Go to section start; skip past length bytes. """
        self.go_to_section_start()
        self.file.seek(4, os.SEEK_CUR)
