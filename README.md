# BogoHTTP

A port of [bogodownload](https://github.com/Roadcrosser/bogodownload) to HTTP for meemz.

## Server demo

```
$ echo 'your mother was a hamster and your father smelt of elderberries' > sick-burn.txt
$ curl -i http://bogo.localhost:8080/sick-burn.txt
HTTP/1.1 206 Partial Content
Content-Range: bytes 6-6/64
Content-Disposition: attachment; filename*=UTF-8''sick-burn.txt
Server: BogoHTTP
Content-Length: 1
Content-Type: application/octet-stream
Date: Mon, 25 Nov 2019 01:42:17 GMT

o⏎
$ curl -i http://bogo.localhost:8080/sick-burn.txt
HTTP/1.1 206 Partial Content
Content-Range: bytes 36-36/64
Content-Disposition: attachment; filename*=UTF-8''sick-burn.txt
Server: BogoHTTP
Content-Length: 1
Content-Type: application/octet-stream
Date: Mon, 25 Nov 2019 01:42:18 GMT

a⏎
```

## Client demo

```
➤ time ./client.py http://bogo.localhost:8080/sick-burn.txt
your mother was a hamster and your father smelt of elderberries
0.51user 0.03system 0:00.75elapsed 73%CPU (0avgtext+0avgdata 27900maxresident)k
0inputs+0outputs (0major+7571minor)pagefaults 0swaps
```

## Installation

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

Starting the server:

```
env BOGOHTTP_BASE_PATH=/path/to/root ./server.py  # relative paths can be used too
```

Should you, for some godforsaken reason, decide to run this in production, follow the [aiohttp.web deployment docs].

[aiohttp.web deployment docs]: https://docs.aiohttp.org/en/stable/deployment.html

Using the client:

```
./client.py http://127.0.0.1:8080/path/to/file
```

This will download /path/to/root/path/to/file, using HTTP request per byte, and output the contents to stdout.

## License

[Blue Oak Model License 1.0.0](https://blueoakcouncil.org/license/1.0.0)
