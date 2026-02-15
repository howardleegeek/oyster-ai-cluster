#!/bin/bash
# Sync infrastructure code to all dispatch nodes

set -e

DISPATCH_DIR=~/Downloads/dispatch
NODES="codex-node-1 glm-node-2 glm-node-3 glm-node-4"

echo "=== Syncing dispatch infrastructure to all nodes ==="

for node in $NODES; do
    echo ">>> Syncing to $node..."
    
    # Sync key files
    rsync -az --delete \
        $DISPATCH_DIR/dispatch.py \
        $DISPATCH_DIR/task-wrapper.sh \
        $DISPATCH_DIR/task-watcher.py \
        $DISPATCH_DIR/nodes.json \
        $DISPATCH_DIR/projects.json \
        ${node}:~/dispatch/
    
    echo ">>> Synced to $node"
done

echo "=== Sync complete ==="

# Verify versions
for node in $NODES; do
    echo "=== $node task-watcher version ==="
    ssh $node "head -5 ~/dispatch/task-watcher.py" 2>/dev/null || echo "Failed to check"
done
