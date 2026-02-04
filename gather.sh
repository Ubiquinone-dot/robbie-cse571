#!/bin/bash
# Record training episodes using lerobot-record

# Load environment variables
set -a
source .env
set +a

# Configuration
TASK="${INSTRUCTION:-Grab the black cube}"
DATASET_NAME="${DATASET:-record-prod5}"
NUM_EPISODES="${NUM_EPISODES:-5}"
FPS="${FPS:-30}"
WIDTH="${WIDTH:-640}"
HEIGHT="${HEIGHT:-480}"

# Extract HF username from HF_REPO_ID
# HF_USER="${HF_REPO_ID%%/*}"
HF_USER=Jbutch

echo "=================================================="
echo "LeRobot Recording"
echo "=================================================="
echo "Leader port:   $LEADER_ARM_PORT"
echo "Follower port: $FOLLOWER_ARM_PORT"
echo "Dataset:       $HF_USER/$DATASET_NAME"
echo "Task:          $TASK"
echo "Episodes:      $NUM_EPISODES"
echo "Resolution:    ${WIDTH}x${HEIGHT} @ ${FPS}fps"
echo "=================================================="

lerobot-record \
    --robot.type=so101_follower \
    --robot.port="$FOLLOWER_ARM_PORT" \
    --robot.id=my_follower \
    --robot.cameras="{ front: {type: opencv, index_or_path: 0, width: $WIDTH, height: $HEIGHT, fps: $FPS}}" \
    --teleop.type=so101_leader \
    --teleop.port="$LEADER_ARM_PORT" \
    --teleop.id=my_leader \
    --display_data=true \
    --dataset.repo_id="$HF_USER/$DATASET_NAME" \
    --dataset.num_episodes="$NUM_EPISODES" \
    --dataset.episode_time_s=15 \
    --dataset.reset_time_s=2 \
    --dataset.single_task="$TASK"
