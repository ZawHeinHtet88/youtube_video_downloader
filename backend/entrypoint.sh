#!/bin/bash

# Start bgutil PO Token server if available
if [ -f /opt/bgutil/server/build/main.js ]; then
    echo "Starting bgutil PO Token server on port 4416..."
    node /opt/bgutil/server/build/main.js --port 4416 &
    sleep 2
    if kill -0 $! 2>/dev/null; then
        echo "bgutil server started (pid=$!)"
    else
        echo "WARNING: bgutil server failed to start"
    fi
else
    echo "WARNING: bgutil server not found at /opt/bgutil/server/build/main.js"
fi

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
