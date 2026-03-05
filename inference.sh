#!/bin/bash
set -e

# Kill any zombie processes from previous runs
./cleanup.sh 2>/dev/null || true

# Load environment variables
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Default values (CHECKPOINT from .env or arg)
CHECKPOINT="${1:-${CHECKPOINT:-ep25}}"
INSTRUCTION="${2:-Grab the black cube}"
N_PICKUPS="${3:-5}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
EVAL_DATASET="${4:-eval_${CHECKPOINT}_${TIMESTAMP}}"

# Extract HF username from HF_REPO_ID (format: username/repo)
HF_USER="${HF_REPO_ID%%/*}"
CAM_IDX="${CAMERA_INDEX:-0}"

# Validate checkpoint exists
POLICY_PATH="checkpoints/${CHECKPOINT}/pretrained_model"
if [ ! -d "$POLICY_PATH" ]; then
    echo "Error: Checkpoint '${CHECKPOINT}' not found"
    echo "Available checkpoints:"
    ls -d checkpoints/*/pretrained_model 2>/dev/null | sed 's|checkpoints/||;s|/pretrained_model||'
    exit 1
fi

# Auto-detect policy type from config.json
POLICY_TYPE="act"
if [ -f "${POLICY_PATH}/config.json" ]; then
    DETECTED=$(python3 -c "import json; print(json.load(open('${POLICY_PATH}/config.json'))['type'])" 2>/dev/null)
    if [ -n "$DETECTED" ]; then
        POLICY_TYPE="$DETECTED"
    fi
fi

echo "Running inference with:"
echo "  Checkpoint: ${CHECKPOINT}"
echo "  Policy type: ${POLICY_TYPE}"
echo "  Policy path: ${POLICY_PATH}"
echo "  Camera index: ${CAM_IDX}"
echo "  Follower port: ${FOLLOWER_ARM_PORT}"
echo "  Task: ${INSTRUCTION}"
echo "  Pickups: ${N_PICKUPS}"
echo "  Dataset: ${HF_USER}/${EVAL_DATASET}"
echo ""

for i in $(seq 1 $N_PICKUPS); do
    echo "=== Pickup $i of $N_PICKUPS ==="

    # Move to home position before inference
    source ./reset.sh

    echo "" | uv run lerobot-record \
        --robot.type=so101_follower \
        --robot.port="${FOLLOWER_ARM_PORT}" \
        --robot.id=my_follower \
        --robot.cameras="{ front: {type: opencv, index_or_path: ${CAM_IDX}, width: 640, height: 480, fps: 30} }" \
        --display_data=false \
        --dataset.repo_id="${HF_USER}/${EVAL_DATASET}_${i}" \
        --dataset.single_task="${INSTRUCTION}" \
        --dataset.push_to_hub=false \
        --dataset.num_episodes=1 \
        --dataset.episode_time_s=20 \
        --dataset.reset_time_s=0 \
        --policy.type="${POLICY_TYPE}" \
        --policy.pretrained_path="${POLICY_PATH}" \
        --policy.device=mps || true
done

source ./reset.sh
./cleanup.sh

echo "=== Completed $N_PICKUPS pickups ==="
