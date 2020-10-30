import struct
from typing import BinaryIO

from .string import read_unicode_string


def read_descriptor(file: BinaryIO):
    """ Some layer records use descriptors to store data. """
    descriptor_data = {}
    name = read_unicode_string(file)
    class_id = read_descriptor_id_string(file)
    num_descriptor_items = struct.unpack('>L', file.read(4))[0]
    for item in range(num_descriptor_items):
        key = read_descriptor_id_string(file)
        os_type_key = struct.unpack('>4s', file.read(4))[0]
        os_type_key = os_type_key.decode('utf-8')

        # Data type in OSType key maps to
        item_value_fn_map = {
            'TEXT': read_descriptor_string,
            'enum': read_descriptor_enumerated,
        }

        item_value_fn = item_value_fn_map[os_type_key]
        item_value = item_value_fn(file)

    return descriptor_data


def read_descriptor_id_string(file: BinaryIO):
    """ Certain ID and key strings in descriptors have a unique format. """
    string_len = struct.unpack('>L', file.read(4))[0]
    if string_len == 0:
        # If length is zero, it has an implied length of 4 bytes
        string_len = 4
    string = struct.unpack(f'>{string_len}s', file.read(string_len))[0]
    string = string.decode('utf-8')
    return string


def read_descriptor_string(file: BinaryIO):
    return read_unicode_string(file)


def read_descriptor_enumerated(file: BinaryIO):
    class_id = read_descriptor_id_string(file)
    type_id = read_descriptor_id_string(file)
    enum = read_descriptor_id_string(file)
    return enum
