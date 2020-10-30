import struct


def unpack_bits(compressed_data: bytes) -> bytes:
    uncompressed_data = bytes()
    pos = 0
    while pos < len(compressed_data):
        header_byte = struct.unpack('b', compressed_data[pos:pos+1])[0]
        pos += 1
        if header_byte == -128:
            continue
        elif header_byte >= 0:
            data_length = header_byte + 1
            for x in range(data_length):
                data = compressed_data[pos:pos+1]
                pos += 1
                uncompressed_data += data
        else:
            data_repeat = 1 - header_byte
            data = compressed_data[pos:pos+1]
            pos += 1
            for x in range(data_repeat):
                uncompressed_data += data
    return uncompressed_data
