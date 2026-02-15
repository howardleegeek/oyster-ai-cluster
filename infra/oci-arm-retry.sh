#!/bin/bash
# OCI ARM A1 Auto-Retry Script
# ARM A1 instances are frequently "Out of host capacity" on free tier.
# This script retries across all 3 ADs every 60 seconds until success.

COMPARTMENT_ID="ocid1.tenancy.oc1..aaaaaaaacxw5myp5gtbn5pzocwl3xw3b4siqmzarslay7pm3dbxsimkfycda"
SUBNET_ID="ocid1.subnet.oc1.phx.aaaaaaaalspfkqumrmnudqh4ttt3upuo3qvo7vagpe52ct4prtt3ajj4duza"
IMAGE_ID="ocid1.image.oc1.phx.aaaaaaaahzur55ghl5ypjy27zsuh7adac4ppnofrp2d3wuxu7iam4ibgkaia"
INSTANCE_NAME="oci-arm-1"
SHAPE="VM.Standard.A1.Flex"
OCPUS=4
MEMORY_GB=24
LOG_FILE="/tmp/oci-arm-retry.log"
SSH_KEY="ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIIIwO4Gi1vG5wJR93FCR+4zO9wrlXxMeoHCoFPLukbHl oci-arm"
export SUPPRESS_LABEL_WARNING=True

ADS=("EotF:PHX-AD-1" "EotF:PHX-AD-2" "EotF:PHX-AD-3")

echo "$(date): Starting ARM A1 auto-retry loop" | tee -a "$LOG_FILE"
echo "Shape: $SHAPE ($OCPUS OCPU, ${MEMORY_GB}GB)" | tee -a "$LOG_FILE"

attempt=0
while true; do
    for ad in "${ADS[@]}"; do
        attempt=$((attempt + 1))
        echo "$(date): Attempt #$attempt - AD: $ad" | tee -a "$LOG_FILE"

        RESULT=$(oci compute instance launch \
            --compartment-id "$COMPARTMENT_ID" \
            --availability-domain "$ad" \
            --shape "$SHAPE" \
            --shape-config "{\"ocpus\": $OCPUS, \"memoryInGBs\": $MEMORY_GB}" \
            --display-name "$INSTANCE_NAME" \
            --image-id "$IMAGE_ID" \
            --subnet-id "$SUBNET_ID" \
            --assign-public-ip true \
            --metadata "{\"ssh_authorized_keys\": \"$SSH_KEY\"}" \
            2>&1) || true

        if echo "$RESULT" | grep -q '"lifecycle-state"'; then
            echo "$(date): SUCCESS! Instance created in $ad" | tee -a "$LOG_FILE"
            echo "$RESULT" | tee -a "$LOG_FILE"
            INSTANCE_ID=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])")
            echo "Instance ID: $INSTANCE_ID" | tee -a "$LOG_FILE"
            echo "$INSTANCE_ID" > /tmp/oci-arm-1-id.txt
            echo "Saved to /tmp/oci-arm-1-id.txt"
            exit 0
        fi

        if echo "$RESULT" | grep -q "Out of host capacity"; then
            echo "$(date): Out of capacity in $ad" | tee -a "$LOG_FILE"
        else
            echo "$(date): Error: $(echo "$RESULT" | grep -o '"message": "[^"]*"' | head -1)" | tee -a "$LOG_FILE"
        fi
    done

    echo "$(date): All ADs tried. Sleeping 60s..." | tee -a "$LOG_FILE"
    sleep 60
done
