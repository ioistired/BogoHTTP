# SPDX-License-Identifier: BlueOak-1.0.0

import urllib.parse
from cgi import parse_header

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
