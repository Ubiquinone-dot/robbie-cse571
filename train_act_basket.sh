#!/bin/bash
#SBATCH --job-name=act_basket
#SBATCH --output=/net/scratch/jbutch/lerobot/act_basket/slurm-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/act_basket/slurm-%j.err
#SBATCH --partition=gpu-train
#SBATCH --gres=gpu:l40:8
#SBATCH --cpus-per-task=32
#SBATCH --mem=512G
#SBATCH --time=72:00:00

# Change to project directory (needed for SLURM)
cd /home/jbutch/Projects/MT25/robbie-cse571

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export PYTHONUNBUFFERED=1
# NCCL workarounds for L40 GPU topology issues
export NCCL_P2P_DISABLE=1
export NCCL_IB_DISABLE=1
export NCCL_SOCKET_IFNAME=lo
export NCCL_DEBUG=WARN

# Configuration
DATASET_REPO="hangyufeng/place_the_basket"
POLICY_USER="Jbutch"
BASE_DIR="/net/scratch/jbutch/lerobot/act_basket"
OUTPUT_DIR="${BASE_DIR}/run"

# Ensure base directory exists for SLURM logs
mkdir -p "$BASE_DIR"

# Generate episode indices (0 to 49, dataset has 50 episodes)
EPISODE_INDICES=$(seq -s ',' 0 49)

echo "=================================================="
echo "LeRobot ACT Training - place_the_basket (8x L40)"
echo "=================================================="
echo "Dataset:    $DATASET_REPO"
echo "Policy:     act"
echo "Output:     $OUTPUT_DIR"
echo "Episodes:   50 (all)"
echo "=================================================="

# Remove old output to avoid FileExistsError
rm -rf "$OUTPUT_DIR"

accelerate launch \
    --multi_gpu \
    --num_processes=8 \
    $(which lerobot-train) \
    --dataset.repo_id=${DATASET_REPO} \
    --dataset.episodes="[$EPISODE_INDICES]" \
    --policy.type=act \
    --output_dir=${OUTPUT_DIR} \
    --job_name=act_basket \
    --policy.device=cuda \
    --wandb.enable=true \
    --policy.repo_id=${POLICY_USER}/act_place_basket

echo ""
echo "=================================================="
echo "ACT training completed!"
echo "=================================================="
