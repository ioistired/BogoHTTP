#!/usr/bin/env python3

# SPDX-License-Identifier: BlueOak-1.0.0

import aiohttp

import headers
from formats import BogoHeader, BogoByte

BUFSIZE = 1024

async def amain():
	import sys
	url = sys.argv[1]
	async with \
		aiohttp.ClientSession(headers={'User-Agent': 'BogoHTTP'}, raise_for_status=True) as sess, \
		sess.get(url) as resp \
	:
		_, filename = headers.parse_content_disposition_header(resp.headers['Content-Disposition'])
		stream = resp.content
		header = await stream.readexactly(BogoHeader.size)
		size, _ = BogoHeader.unpack(header)

		# TODO write to a file, with a .part file indicating which bytes have been downloaded so far
		f = bytearray(size)
		# has_downloaded[pos] is True if f[pos] has been downloaded yet
		# TODO use something more memory efficient, like an array.array('I')
		has_downloaded = [False] * size
		bytes_downloaded = 0

		while bytes_downloaded < size:
			data = await stream.readexactly(BogoByte.size)
			pos, byte = BogoByte.unpack(data)

			if has_downloaded[pos]:
				continue

			f[pos] = byte
			has_downloaded[pos] = True
			bytes_downloaded += 1

	for chunk_start in range(0, size+(size//BUFSIZE+1), BUFSIZE):
		sys.stdout.buffer.write(f[chunk_start:chunk_start+BUFSIZE])

def main():
	import asyncio
	asyncio.get_event_loop().run_until_complete(amain())

if __name__ == '__main__':
	main()
