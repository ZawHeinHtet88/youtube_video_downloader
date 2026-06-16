#!/bin/bash
set -e

echo "Starting bgutil PO Token server on port 4416..."
node /opt/bgutil/server/build/main.js --port 4416 &
BGUTIL_PID=$!
sleep 2

if kill -0 $BGUTIL_PID 2>/dev/null; then
    echo "bgutil server started (pid=$BGUTIL_PID)"
else
    echo "WARNING: bgutil server failed to start"
fi

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
