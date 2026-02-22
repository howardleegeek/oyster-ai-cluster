#!/bin/bash
# Deploy Temporal workers to all remote nodes
# Workers connect back to the Mac's Temporal server via Tailscale

TEMPORAL_HOST="100.95.165.3:7233"
TASK_QUEUE="dispatch-tasks"
WORKER_DIR="temporal-worker"

# Files to deploy
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

NODES=(
    "codex-node-1:20"
    "glm-node-2:20"
    "glm-node-3:20"
    "glm-node-4:20"
    "howard-mac2:10"
    "gcp-new-1:10"
    "gcp-new-2:10"
    "gcp-new-3:10"
    "gcp-new-4:20"
    "upcloud-1:20"
    "aws-spot-1:20"
    "aws-spot-4:20"
)

deploy_worker() {
    local host="${1%%:*}"
    local slots="${1##*:}"
    local name="${host}"

    echo "[$name] Deploying worker (slots=$slots)..."

    # Create worker dir
    ssh -o ConnectTimeout=5 "$host" "mkdir -p ~/$WORKER_DIR" 2>/dev/null
    if [ $? -ne 0 ]; then
        echo "[$name] SKIP: SSH connect failed"
        return 1
    fi

    # Copy worker files + task-wrapper.sh
    scp -q "$SCRIPT_DIR/workflows.py" "$SCRIPT_DIR/activities.py" "$SCRIPT_DIR/worker.py" "$host:~/$WORKER_DIR/" 2>/dev/null
    # task-wrapper.sh goes to ~/dispatch/ (where DISPATCH_DIR resolves on remote nodes)
    ssh "$host" "mkdir -p ~/dispatch" 2>/dev/null
    scp -q "$SCRIPT_DIR/task-wrapper.sh" "$host:~/dispatch/task-wrapper.sh" 2>/dev/null

    # Install temporalio if needed
    ssh "$host" "pip3 install temporalio pyyaml 2>/dev/null | tail -1" 2>/dev/null

    # Kill any existing temporal worker
    ssh "$host" "pkill -f 'python3.*worker.py.*dispatch-tasks' 2>/dev/null; sleep 1" 2>/dev/null

    # Start worker with env vars (edge nodes = activity-only, no workflow hosting)
    ssh "$host" "cd ~/$WORKER_DIR && \
        TEMPORAL_HOST=$TEMPORAL_HOST \
        TASK_QUEUE=$TASK_QUEUE \
        WORKER_NAME=$name \
        MAX_CONCURRENT=$slots \
        WORKER_ROLE=activity \
        MINIMAX_API_KEY=\"${MINIMAX_API_KEY}\" \
        ANTHROPIC_API_KEY=\"${ANTHROPIC_API_KEY}\" \
        OPENAI_API_KEY=\"${OPENAI_API_KEY}\" \
        nohup python3 worker.py > ~/temporal-worker.log 2>&1 &
        echo \"Worker PID: \$!\"" 2>/dev/null

    if [ $? -eq 0 ]; then
        echo "[$name] OK - worker started (slots=$slots)"
    else
        echo "[$name] FAILED to start worker"
    fi
}

echo "=== Deploying Temporal Workers ==="
echo "Temporal Server: $TEMPORAL_HOST"
echo "Task Queue: $TASK_QUEUE"
echo ""

for node in "${NODES[@]}"; do
    deploy_worker "$node" &
done

wait
echo ""
echo "=== Deploy Complete ==="
