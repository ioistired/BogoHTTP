#!/usr/bin/env python3

import urllib.parse
from cgi import parse_header

import aiohttp

BUFSIZE = 1024

def parse_content_range_header(h):
	# https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Range
	unit, rest = h.split(None, 1)
	range_, slash, length = rest.partition('/')
	start, hyphen, stop = range_.partition('-')
	return range(int(start), int(stop)+1), int(length)

def parse_content_disposition_header(h):
	# https://github.com/jeroen/curl/issues/187
	# https://tools.ietf.org/html/rfc5987#section-3.2.2
	disposition, params = parse_header(h)
	is_extended = 'filename*' in params
	try:
		extended_form_filename = params['filename*']
	except KeyError:
		return disposition, params['filename']
	else:
		return disposition, parse_extended_content_disposition_filename(extended_form_filename)

def parse_extended_content_disposition_filename(value):
	end_of_encoding = first_tick = value.index("'")
	encoding = value[:end_of_encoding]

	end_of_language = value.index("'", end_of_encoding+1)
	language = value[first_tick:end_of_language]

	# don't bother supporting quoted filenames
	filename = value[end_of_language+1:]

	return urllib.parse.unquote(filename, encoding=encoding)

async def amain():
	import sys
	url = sys.argv[1]
	async with aiohttp.ClientSession(headers={'User-Agent': 'BogoHTTP'}, raise_for_status=True) as sess:
		async with sess.head(url) as resp:
			_, size = parse_content_range_header(resp.headers['Content-Range'])
			_, filename = parse_content_disposition_header(resp.headers['Content-Disposition'])
		f = bytearray(size)
		has_downloaded = [False] * size  # each index is true if the byte at that position has been downloaded already
		bytes_downloaded = 0

		while bytes_downloaded < size:
			async with sess.get(url) as resp:
				content_range, _ = parse_content_range_header(resp.headers['Content-Range'])
				i = content_range.start
				if has_downloaded[i]:
					continue
				f[i] = (await resp.read())[0]
				has_downloaded[i] = True
				bytes_downloaded += 1

	for chunk_start in range(0, size//BUFSIZE + 1, BUFSIZE):
		sys.stdout.buffer.write(f[chunk_start:chunk_start+BUFSIZE])

def main():
	import asyncio
	asyncio.get_event_loop().run_until_complete(amain())

if __name__ == '__main__':
	main()
