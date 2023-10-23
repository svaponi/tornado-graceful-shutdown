#!/bin/bash
set -euo pipefail

pushd "$(dirname "$0")" >/dev/null


#endpoint="blocking"
endpoint="async"

# start the server on a separate process
python server.py &
pid=$!

# wait for the sever to start
sleep 1

# start long running requests
curl -sSL "http://localhost:8888/${endpoint}?delay=10" >/dev/null &
curl -sSL "http://localhost:8888/${endpoint}?delay=7" >/dev/null &
curl -sSL "http://localhost:8888/${endpoint}?delay=4" >/dev/null &

# wait for the request to be accepted from the sever
sleep 1

# stop the sever before the request terminates
kill -s SIGTERM $pid

# try another request, should return 410 Gone or curl error "Failed to connect"
curl -sSL "http://localhost:8888/${endpoint}?delay=5" &

# wait for the server process to stop
wait $pid

echo "server stopped"
