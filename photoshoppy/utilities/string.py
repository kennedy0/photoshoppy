import os
import struct
from collections import namedtuple
from typing import BinaryIO

PascalString = namedtuple("PascalString", "count value")


def unpack_string(s: bytes, length: int, encoding: str = 'utf-8') -> str:
    string = struct.unpack(f'>{length}s', s)[0]
    string = string.decode(encoding)
    return string


def read_pascal_string(file: BinaryIO, padding=None) -> PascalString:
    """ Read a Pascal string at the current position in file.
    If padding is not None, file position will advance to the end of the padding length.
    """
    # Read first byte to determine string length
    count = struct.unpack('B', file.read(1))[0]
    file.seek(-1, os.SEEK_CUR)

    # If count is 0, it is a null name.
    if count == 0:
        return PascalString(0, "")

    # Read Pascal string
    pstring_length = count + 1
    value = struct.unpack(f'{pstring_length}p', file.read(pstring_length))[0]
    value = value.decode('utf-8')

    # Handle byte padding.
    if padding is not None:
        rem = pstring_length % padding
        if rem == 0:
            pass
        else:
            file.seek(padding - rem, os.SEEK_CUR)

    return PascalString(count, value)


def read_unicode_string(file: BinaryIO) -> str:
    """ Read a unicode string. All values defined as Unicode string consist of:
    A 4-byte length field, representing the number of UTF-16 code units in the string (not bytes).
    The string of Unicode values, two bytes per character, and a two byte null for the end of the string.
    """
    ustring_length = struct.unpack('>L', file.read(4))[0]
    bytes_length = ustring_length * 2
    ustring = struct.unpack(f'{bytes_length}s', file.read(bytes_length))[0]
    ustring = ustring.decode('utf-16-be')
    return ustring
