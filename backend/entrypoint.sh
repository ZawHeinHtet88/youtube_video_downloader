#!/bin/bash

# Try to start bgutil PO Token server
BGUTIL_DIR="/opt/bgutil/server"

if [ ! -f "$BGUTIL_DIR/build/main.js" ]; then
    echo "Building bgutil server from source..."
    if [ -d "/opt/bgutil/repo/server" ]; then
        cd /opt/bgutil/repo/server
        npm install --no-audit --no-fund 2>&1 | tail -3
        npx tsc 2>&1 | tail -3
        if [ -f build/main.js ]; then
            mkdir -p "$BGUTIL_DIR"
            cp -r build node_modules package.json "$BGUTIL_DIR/"
            echo "bgutil server built successfully"
        fi
    fi
fi

if [ -f "$BGUTIL_DIR/build/main.js" ]; then
    echo "Starting bgutil PO Token server on port 4416..."
    node "$BGUTIL_DIR/build/main.js" --port 4416 &
    sleep 2
    echo "bgutil server started"
else
    echo "WARNING: bgutil server not available"
fi

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
