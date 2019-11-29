# BogoHTTP

A port of [bogodownload](https://github.com/Roadcrosser/bogodownload) to HTTP for meemz.

## Demo

```
$ dd if=/dev/urandom bs=1000 count=200 of=random-200KB.bin
200+0 records in
200+0 records out
200000 bytes (200 kB, 195 KiB) copied, 0.00533823 s, 37.5 MB/s
$ env BOGOHTTP_BASE_PATH=. ./server.py &
$ ======== Running on http://0.0.0.0:8080 ========
(Press CTRL+C to quit)

$ time ./client.py http://bogo.localhost:8080/random-200KB.bin > random-200KB-transferred.bin
26.41user 2.08system 0:29.17elapsed 97%CPU (0avgtext+0avgdata 29356maxresident)k
0inputs+392outputs (0major+7504minor)pagefaults 0swaps
$ sha256sum random-100KB.bin random-100KB-transferred.bin 
fc54eacf0dcfa05695f36a04c5f3f6447da197ccc04750b14d8ff800a2eb1138  random-100KB.bin
fc54eacf0dcfa05695f36a04c5f3f6447da197ccc04750b14d8ff800a2eb1138  random-100KB-transferred.bin
$ py 200/30
6.666666666666667
$ # a mere 6 KB/s on localhost !!
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

This will download /path/to/root/path/to/file and output the contents to stdout.

## License

[Blue Oak Model License 1.0.0](https://blueoakcouncil.org/license/1.0.0)
