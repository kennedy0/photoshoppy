import os
import struct
from typing import BinaryIO

from photoshoppy.utilities.string import unpack_string
from .constants import get_description


class ImageResourceBlock:
    def __init__(self, file: BinaryIO):
        self._file = file
        self._offset = file.tell()
        self._resource_id = None
        self._name = None
        self._description = None
        self._resource_data = None

        self._read_block()

    @property
    def offset(self) -> int:
        return self._offset

    @property
    def resource_id(self) -> int:
        return self._resource_id

    @property
    def name(self) -> str or None:
        return self._name

    @property
    def description(self) -> str:
        return self._description

    @property
    def resource_data(self):
        return self._resource_data

    def _read_block(self):
        self._read_signature()
        self._resource_id = struct.unpack('>H', self._file.read(2))[0]
        self._description = get_description(self.resource_id)
        self._name = self._read_name()
        self._read_resource_data()

    def _read_signature(self):
        """ Read and validate the signature of this resource block. """
        signature = unpack_string(self._file.read(4), length=4)
        assert signature == "8BIM"

    def _read_name(self) -> str or None:
        """ Name is a Pascal string, padded out make the size even.
        Null name consists of two bytes of 0x00.
        """
        # Read first byte to determine string length
        count = struct.unpack('B', self._file.read(1))[0]
        self._file.seek(-1, os.SEEK_CUR)

        # If count is 0, it is a null name.
        if count == 0:
            self._file.seek(2, os.SEEK_CUR)
            return None

        # Read Pascal string
        pstring_length = count + 1
        name = struct.unpack(f'{pstring_length}p', self._file.read(pstring_length))[0]
        name = name.decode('utf-8')

        # Names are padded to make the size even.
        if pstring_length % 2 != 0:
            self._file.seek(1, os.SEEK_CUR)

        return name

    def _read_resource_data(self):
        size = struct.unpack('>L', self._file.read(4))[0]

        # Skip resource data for now.
        self._file.seek(size, os.SEEK_CUR)

        # Resource data is padded to make the size even.
        if size % 2 != 0:
            self._file.seek(1, os.SEEK_CUR)
