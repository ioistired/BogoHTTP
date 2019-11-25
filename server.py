#!/usr/bin/env python3

# SPDX-License-Identifier: BlueOak-1.0.0

import io
import typing
import random
import urllib.parse
from functools import partial
from pathlib import Path

from aiohttp import web

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

def random_byte(f: typing.BinaryIO, length: int):
	"""Return one random byte from a file. position is not preserved.
	If the file is empty, return b''.
	"""
	len = file_size(f)
	if len == 0:
		return b''
	f.seek(random.randrange(0, len))
	return f.read(1)

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
		b = random_byte(f, length=total_size)
		range = file_range(f, b)
		# HTTP requires a Range header in the request in order to return Partial Content.
		# However, we require a custom client to transfer a file as it is.
		return web.HTTPPartialContent(
			body=b,
			headers={
				'Content-Range': content_range_header(range, length=total_size),
				'Content-Disposition': content_disposition_header(path),
			},
		)

def get_app():
	import os, types
	app = web.Application(middlewares=[advertise_self])
	app['config'] = types.SimpleNamespace()
	app['config'].base_path = Path(os.environ['BOGOHTTP_BASE_PATH']).resolve(strict=True)
	app.add_routes(routes)
	return app

async def app():
	return get_app()

if __name__ == '__main__':
	web.run_app(get_app())
