#!/usr/bin/env python3

# SPDX-License-Identifier: BlueOak-1.0.0

import io
import typing
import random
import struct
import urllib.parse
from functools import partial
from pathlib import Path

from aiohttp import web

from formats import BogoHeader, BogoByte

routes = web.RouteTableDef()

# configuration is done via environment variables.
# required vars:
#    - BOGOHTTP_BASE_PATH: str = root of all files to serve
# optional keys:
#    - BOGOHTTP_CHUNK_SIZE: int = how many bytes to return in each response.
#      Defaults to 1 byte.
#      This feature is not implemented yet.

@web.middleware
async def advertise_self(request, handler):
	resp = await handler(request)
	server_header = resp.headers.get('Server', '')
	resp.headers['Server'] = 'BogoHTTP' + server_header
	return resp

def ensure_beneath(base_path, path):
	try:
		resolved = (base_path / path).resolve()
	except RuntimeError:  # symlink recursion
		raise web.HTTPForbidden

	if base_path not in resolved.parents:
		print(list(resolved.parents))
		raise web.HTTPForbidden

	return resolved

def ensure_safe(request, path):
	p = ensure_beneath(request.app['config'].base_path, Path(path))
	if not p.exists():
		raise web.HTTPNotFound
	if not p.is_file():
		raise web.HTTPBadRequest
	return p

PATH_REGEX = r'[^/].+?'

def file_size(f: typing.BinaryIO) -> int:
	f.seek(0, io.SEEK_END)
	return f.tell()

def file_range(f: typing.BinaryIO, data: bytes) -> slice:
	"""Given a file and data read from that file, return a slice representing the range that was just read from it.
	No slice attributes will be None. Step will always be 1.
	"""
	cur_pos = f.tell()
	start_pos = cur_pos - len(data)
	return slice(start_pos, cur_pos, 1)

def content_range_header(range: typing.Union[slice, range], *, length) -> str:
	return f'bytes {range.start}-{range.stop-1}/{length}'

def content_disposition_header(path, *, disposition='attachment') -> str:
	return f"{disposition}; filename*=UTF-8''{urllib.parse.quote(path.name.encode('utf-8'))}"

@routes.get('/{path:%s}' % PATH_REGEX)
async def get(request):
	path = ensure_safe(request, request.match_info['path'])

	with open(path, 'rb', buffering=0) as f:
		total_size = file_size(f)

		resp = web.StreamResponse()
		# note: we can't use the Content-Length header because that indicates that we'll close the response
		# after N bytes.
		resp.headers['Content-Disposition'] = content_disposition_header(path)
		resp.headers['Content-Type'] = 'application/bogo-http'
		await resp.prepare(request)  # send headers to the client

		if total_size == 0:
			await resp.write(BogoHeader.pack(0, 0))
			await resp.send_eof()
			return

		await resp.write(BogoHeader.pack(total_size, 0))

		while True:
			pos = random.randrange(0, total_size)
			f.seek(pos)
			b = f.read(1)[0]  # f.read() returns a bytes object and the first element is an integer
			await resp.write(BogoByte.pack(pos, b))

def get_app():
	import os, types
	app = web.Application(middlewares=[advertise_self])
	app['config'] = types.SimpleNamespace()
	base_path = Path(os.environ['BOGOHTTP_BASE_PATH'])
	if not base_path.is_absolute():
		raise RuntimeError('BOGOHTTP_BASE_PATH must be absolute')
	app['config'].base_path = base_path.resolve(strict=True)
	app.add_routes(routes)
	return app

async def app():
	return get_app()

if __name__ == '__main__':
	web.run_app(get_app())
