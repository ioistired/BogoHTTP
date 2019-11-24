#!/usr/bin/env python3

# SPDX-License-Identifier: BlueOak-1.0.0

import io
import typing
import random
from functools import partial
from pathlib import Path

from aiohttp import web

app = web.Application()
routes = web.RouteTableDef()

# config file structure: one top level dict
# acceptable keys:
#    - base_path: str = root of all files to serve

with open('config.py') as f:
	config = eval(f.read(), {})

def ensure_beneath(base_path, path):
	try:
		resolved = (base_path / path).resolve()
	except RuntimeError:  # symlink recursion
		raise web.HTTPForbidden

	if base_path not in resolved.parents:
		raise web.HTTPForbidden

	return resolved

ensure_in_base_path = partial(ensure_beneath, config['base_path'])

def ensure_safe(path):
	p = ensure_beneath(Path(value))
	if not p.exists():
		raise web.HTTPNotFound
	if not p.is_file():
		raise web.HTTPBadRequest
	return p

PATH_REGEX = r'[^/].+?'

def size(f: typing.BinaryIO):
	f.seek(0, io.SEEK_END)
	return f.tell()

def random_byte(f: typing.BinaryIO):
	len = size(f)
	if len == 0:
		return b''
	f.seek(random.randrange(0, len))
	return f.read(1)

@routes.get('/{path:%s}' % PATH_REGEX)
async def get(request):
	path = ensure_safe(request.match_info['path'])

	with open(path) as f:
		...

app.add_routes(routes)
