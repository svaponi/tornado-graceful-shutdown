# tornado-graceful-shutdown

How to prevent [tornado](https://www.tornadoweb.org/en/stable/) from interrupting long-running non-blocking requests
when it receives a termination signal? See [server.py](server.py).

Create and activate virtual env.

```bash
python3 -m pip install virtualenv
python3 -m venv .venv
source .venv/bin/activate
```

Install requirements.

```bash
pip install -r requirements.txt
```

Start the server.

```bash
python server.py
```

> Press `Ctrl+C` to send `SIGINT`.

Run server and tests.

```bash
./test.sh
```