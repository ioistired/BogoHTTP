# SPDX-License-Identifier: BluOak-1.0.0

import struct

# position, followed by one byte (the payload)
# in little-endian format
BogoByte = struct.Struct('<iB')

# the first thing sent to the client has the same format, but a different meaning:
# total size of file, followed by a null byte
BogoHeader = BogoByte
