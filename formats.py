# SPDX-License-Identifier: BlueOak-1.0.0

import struct

N = 64
NBYTES = N // 8
MAX_SIZE = 1 << (N - 8)

def pack(pos, byte: int) -> bytes:
	pos = pos & ((1 << (N - 8)) - 1)  # truncate to N-8 bytes
	return struct.pack('<L', pos << 8 | byte)

def unpack(bytes: bytes) -> (int, int):
	n, = struct.unpack_from('<L', bytes)
	pos = n >> 8
	byte = n & ((1 << 8) - 1)
	return pos, byte
