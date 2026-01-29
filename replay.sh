#!/bin/bash
# Replay recorded episodes using lerobot-replay

# Load environment variables
set -a
source .env
set +a

# Configuration
DATASET_NAME="${DATASET:-record-prod}"
EPISODE="${EPISODE:-0}"
HF_USER="${HF_USER:-Jbutch}"

echo "=================================================="
echo "LeRobot Replay"
echo "=================================================="
echo "Follower port: $FOLLOWER_ARM_PORT"
echo "Dataset:       $HF_USER/$DATASET_NAME"
echo "Episode:       $EPISODE"
echo "=================================================="

lerobot-replay \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_ARM_PORT" \
    --robot.id=my_follower \
    --dataset.repo_id="$HF_USER/$DATASET_NAME" \
    --dataset.episode="$EPISODE"
