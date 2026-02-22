#!/bin/bash
# OCI ARM A1 Flex instance grabber
# Retries every 60 seconds across all 3 ADs until successful
# Usage: ./oci-arm-grab.sh (or via launchd)

set -euo pipefail

COMPARTMENT="ocid1.tenancy.oc1..aaaaaaaacxw5myp5gtbn5pzocwl3xw3b4siqmzarslay7pm3dbxsimkfycda"
SUBNET="ocid1.subnet.oc1.phx.aaaaaaaalspfkqumrmnudqh4ttt3upuo3qvo7vagpe52ct4prtt3ajj4duza"
IMAGE="ocid1.image.oc1.phx.aaaaaaaaf6r2o2eybs2cnlmrhfnmzg546g2tpy3estztocaugnp7egxabmlq"
SSH_KEY="$HOME/.ssh/oci_arm.pub"
INSTANCE_NAME="oci-arm-1"
SHAPE="VM.Standard.A1.Flex"
OCPUS=4
MEMORY_GB=24
ADS=("EotF:PHX-AD-1" "EotF:PHX-AD-2" "EotF:PHX-AD-3")
LOG="$HOME/Downloads/dispatch/oci-arm-grab.log"
INTERVAL=60

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" | tee -a "$LOG"
}

# Check if instance already exists
check_existing() {
    local result
    result=$(oci compute instance list \
        --compartment-id "$COMPARTMENT" \
        --display-name "$INSTANCE_NAME" \
        --lifecycle-state RUNNING \
        --query 'data[0].id' \
        --raw-output 2>/dev/null || true)
    if [[ -n "$result" && "$result" != "null" && "$result" != "None" ]]; then
        return 0
    fi
    return 1
}

try_launch() {
    local ad="$1"
    log "Trying $ad..."

    local output
    output=$(oci compute instance launch \
        --compartment-id "$COMPARTMENT" \
        --availability-domain "$ad" \
        --shape "$SHAPE" \
        --shape-config "{\"ocpus\": $OCPUS, \"memoryInGBs\": $MEMORY_GB}" \
        --display-name "$INSTANCE_NAME" \
        --image-id "$IMAGE" \
        --subnet-id "$SUBNET" \
        --assign-public-ip true \
        --ssh-authorized-keys-file "$SSH_KEY" \
        2>&1)

    local rc=$?
    if [[ $rc -eq 0 ]]; then
        log "SUCCESS on $ad!"
        log "$output"

        # Extract instance ID and wait for public IP
        local instance_id
        instance_id=$(echo "$output" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null || true)
        if [[ -n "$instance_id" ]]; then
            log "Instance ID: $instance_id"
            log "Waiting for public IP (may take 1-2 min)..."
            sleep 60
            local ip
            ip=$(oci compute instance list-vnics \
                --instance-id "$instance_id" \
                --query 'data[0]."public-ip"' \
                --raw-output 2>/dev/null || true)
            log "Public IP: ${ip:-pending}"
        fi
        return 0
    else
        if echo "$output" | grep -q "Out of host capacity"; then
            log "No capacity on $ad"
        elif echo "$output" | grep -q "timed out"; then
            log "Timeout on $ad"
        else
            log "Error on $ad: $(echo "$output" | head -3)"
        fi
        return 1
    fi
}

# Main loop
log "=== OCI ARM Grabber started ==="
log "Target: $INSTANCE_NAME ($SHAPE, ${OCPUS} OCPU, ${MEMORY_GB}GB RAM)"

attempt=0
while true; do
    # Check if already created
    if check_existing; then
        log "Instance $INSTANCE_NAME already running. Exiting."
        exit 0
    fi

    attempt=$((attempt + 1))
    log "--- Attempt #$attempt ---"

    # Try each AD
    for ad in "${ADS[@]}"; do
        if try_launch "$ad"; then
            log "=== Instance created! Grabber done. ==="
            exit 0
        fi
        sleep 5
    done

    log "All ADs full. Retrying in ${INTERVAL}s..."
    sleep "$INTERVAL"
done
