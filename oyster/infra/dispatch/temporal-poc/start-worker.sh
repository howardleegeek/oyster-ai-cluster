#!/bin/bash
# Start Temporal worker on a node
# Usage: bash start-worker.sh [TEMPORAL_HOST] [WORKER_NAME]
TEMPORAL_HOST="${1:-localhost:7233}"
WORKER_NAME="${2:-$(hostname)}"
REMOTE_DIR="$HOME/temporal-worker"
cd "$REMOTE_DIR"

# Setup venv if needed
if [[ ! -d .venv ]]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -q -r requirements.txt 2>/dev/null

# Kill existing worker
pkill -f "temporal-worker/worker.py" 2>/dev/null || true
sleep 1

# Start worker with unbuffered output
export TEMPORAL_HOST="$TEMPORAL_HOST"
export WORKER_NAME="$WORKER_NAME"
export MAX_CONCURRENT="${MAX_CONCURRENT:-8}"
export PYTHONUNBUFFERED=1
nohup python3 worker.py > worker.log 2>&1 &
WPID=$!
sleep 2

# Verify
if kill -0 $WPID 2>/dev/null; then
    echo "OK: worker PID=$WPID on $WORKER_NAME"
else
    echo "FAIL: worker died. Log:"
    tail -10 worker.log 2>/dev/null
fi
