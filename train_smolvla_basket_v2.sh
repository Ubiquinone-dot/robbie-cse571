#!/bin/bash
#SBATCH --job-name=smolvla_basket_v2
#SBATCH --output=/net/scratch/jbutch/lerobot/smolvla_basket_v2/slurm-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/smolvla_basket_v2/slurm-%j.err
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
export TOKENIZERS_PARALLELISM=false

# Configuration
DATASET_REPO="hangyufeng/place_the_basket"
POLICY_USER="Jbutch"
BASE_DIR="/net/scratch/jbutch/lerobot/smolvla_basket_v2"
OUTPUT_DIR="${BASE_DIR}/run"

# Ensure base directory exists for SLURM logs
mkdir -p "$BASE_DIR"

# Generate episode indices (0 to 49, dataset has 50 episodes)
EPISODE_INDICES=$(seq -s ',' 0 49)

echo "=================================================="
echo "LeRobot SmolVLA v2 Training - place_the_basket (8x L40)"
echo "Tuned: lower LR, longer warmup, larger batch"
echo "=================================================="

# Remove old output to avoid FileExistsError
rm -rf "$OUTPUT_DIR"

accelerate launch \
    --multi_gpu \
    --num_processes=8 \
    --main_process_port=29502 \
    $(which lerobot-train) \
    --dataset.repo_id=${DATASET_REPO} \
    --dataset.episodes="[$EPISODE_INDICES]" \
    --policy.path=lerobot/smolvla_base \
    --output_dir=${OUTPUT_DIR} \
    --job_name=smolvla_basket_v2 \
    --policy.device=cuda \
    --batch_size=8 \
    --wandb.enable=true \
    --policy.use_amp=true \
    --policy.optimizer_lr=5e-5 \
    --policy.scheduler_warmup_steps=2000 \
    --policy.scheduler_decay_steps=50000 \
    --rename_map='{"observation.images.follower_arm": "observation.images.camera1"}' \
    --policy.empty_cameras=2 \
    --policy.repo_id=${POLICY_USER}/smolvla_place_basket_v2

echo ""
echo "=================================================="
echo "SmolVLA v2 training completed!"
echo "=================================================="
