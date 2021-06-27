import struct


def get_bit_width(interpreter_path):
    size = struct.calcsize('P') * 8
    return 'x86' if size == 32 else 'x64'
