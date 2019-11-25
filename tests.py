import io
import random
import pytest

import server
import client

def test_random_byte():
	data = b'isogram'
	f = io.BytesIO(data)
	seen = set()
	while True:
		byte = server.random_byte(f)
		assert byte in data
		seen.add(byte)
		if len(seen) == len(data):  # assume data is an isogram
			break

def test_random_byte_on_empty_file():
	assert server.random_byte(io.BytesIO()) == b''
