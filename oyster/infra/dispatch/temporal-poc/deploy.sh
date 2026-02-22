#!/usr/bin/env bash
set -euo pipefail

# Deploy Temporal worker to all cluster nodes
# Usage: bash deploy.sh [node1 node2 ...]
# If no nodes specified, deploys to all nodes in nodes.json

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DISPATCH_DIR="$(dirname "$SCRIPT_DIR")"
NODES_JSON="$DISPATCH_DIR/nodes.json"
TEMPORAL_HOST="${TEMPORAL_HOST:-100.95.165.3:7233}"

# Files to deploy
FILES=(
    "$SCRIPT_DIR/workflows.py"
    "$SCRIPT_DIR/activities.py"
    "$SCRIPT_DIR/worker.py"
    "$SCRIPT_DIR/cli.py"
    "$SCRIPT_DIR/requirements.txt"
)

# Get node list
if [[ $# -gt 0 ]]; then
    NODES=("$@")
else
    if [[ ! -f "$NODES_JSON" ]]; then
        echo "ERROR: No nodes specified and $NODES_JSON not found"
        exit 1
    fi
    NODES=($(python3 -c "
import json
with open('$NODES_JSON') as f:
    data = json.load(f)
nodes = data.get('nodes', data) if isinstance(data, dict) else data
for n in nodes:
    host = n.get('ssh_host')
    if host and n.get('slots', 0) > 0:
        print(host)
"))
fi

echo "=== Temporal Worker Deployment ==="
echo "Temporal Host: $TEMPORAL_HOST"
echo "Nodes: ${NODES[*]}"
echo "Files: ${#FILES[@]}"
echo ""

REMOTE_DIR="\$HOME/temporal-worker"
SUCCESS=0
FAIL=0

for node in "${NODES[@]}"; do
    echo "--- Deploying to $node ---"

    # Create remote directory
    ssh -o ConnectTimeout=5 "$node" "mkdir -p $REMOTE_DIR" 2>/dev/null || {
        echo "  SKIP: Cannot connect to $node"
        FAIL=$((FAIL + 1))
        continue
    }

    # Copy files
    for f in "${FILES[@]}"; do
        scp -q "$f" "$node:$REMOTE_DIR/" 2>/dev/null
    done

    # Install deps + start worker
    ssh "$node" bash -s "$TEMPORAL_HOST" "$node" <<'REMOTE_SCRIPT'
TEMPORAL_HOST="$1"
WORKER_NAME="$2"
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

# Verify it's still running
if kill -0 $WPID 2>/dev/null; then
    echo "  OK: worker PID=$WPID on $WORKER_NAME"
else
    echo "  FAIL: worker died immediately. Log:"
    cat worker.log 2>/dev/null | tail -10
fi
REMOTE_SCRIPT

    echo "  Done: $node"
    SUCCESS=$((SUCCESS + 1))
done

echo ""
echo "=== Deployment Complete ==="
echo "Success: $SUCCESS / $((SUCCESS + FAIL))"
echo "Check: ssh <node> 'ps aux | grep worker.py'"
echo "Temporal UI: http://localhost:8088"
