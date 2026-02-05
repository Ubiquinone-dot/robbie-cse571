#!/bin/bash
set -e

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Default values
CHECKPOINT="${1:-ep25}"
INSTRUCTION="${2:-pick up the black cube}"
N_PICKUPS="${3:-5}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EVAL_DATASET="${4:-eval_${CHECKPOINT}_${TIMESTAMP}}"

# Extract HF username from HF_REPO_ID (format: username/repo)
HF_USER="${HF_REPO_ID%%/*}"

# Validate checkpoint exists
POLICY_PATH="checkpoints/${CHECKPOINT}/pretrained_model"
if [ ! -d "$POLICY_PATH" ]; then
    echo "Error: Checkpoint '${CHECKPOINT}' not found"
    echo "Available checkpoints:"
    ls -d checkpoints/*/pretrained_model 2>/dev/null | sed 's|checkpoints/||;s|/pretrained_model||'
    exit 1
fi

echo "Running inference with:"
echo "  Checkpoint: ${CHECKPOINT}"
echo "  Policy path: ${POLICY_PATH}"
echo "  Follower port: ${FOLLOWER_ARM_PORT}"
echo "  Task: ${INSTRUCTION}"
echo "  Pickups: ${N_PICKUPS}"
echo "  Dataset: ${HF_USER}/${EVAL_DATASET}"
echo ""

for i in $(seq 1 $N_PICKUPS); do
    echo "=== Pickup $i of $N_PICKUPS ==="

    # Move to home position before inference
    source ./reset.sh

    uv run lerobot-record \
        --robot.type=so101_follower \
        --robot.port="${FOLLOWER_ARM_PORT}" \
        --robot.id=my_follower \
        --robot.cameras='{ front: {type: opencv, index_or_path: 0, width: 640, height: 480, fps: 30} }' \
        --display_data=false \
        --dataset.repo_id="${HF_USER}/${EVAL_DATASET}_${i}" \
        --dataset.single_task="${INSTRUCTION}" \
        --dataset.push_to_hub=false \
        --dataset.num_episodes=1 \
        --dataset.episode_time_s=20 \
        --dataset.reset_time_s=0 \
        --policy.type=act \
        --policy.pretrained_path="${POLICY_PATH}" \
        --policy.device=mps || true

done

echo "=== Completed $N_PICKUPS pickups ==="
