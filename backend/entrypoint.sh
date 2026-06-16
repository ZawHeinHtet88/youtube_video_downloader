#!/bin/bash
set -e

echo "Starting bgutil PO Token server on port 4416..."
if [ -f /opt/bgutil/server/build/main.js ]; then
    node /opt/bgutil/server/build/main.js --port 4416 &
    BGUTIL_PID=$!
    sleep 3
    if kill -0 $BGUTIL_PID 2>/dev/null; then
        echo "bgutil server started (pid=$BGUTIL_PID)"
    else
        echo "WARNING: bgutil server failed to start, continuing without it"
    fi
else
    echo "WARNING: bgutil server not found at /opt/bgutil/server/build/main.js"
fi

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
