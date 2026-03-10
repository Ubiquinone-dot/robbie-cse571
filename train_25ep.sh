#!/bin/bash
#SBATCH --job-name=act_so101_ep25
#SBATCH --output=/net/scratch/jbutch/lerobot/multi/slurm-ep25-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/multi/slurm-ep25-%j.err
#SBATCH --partition=gpu-train
#SBATCH --gres=gpu:l40:2
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=24:00:00

# Activate virtual environment
source .venv/bin/activate

# Configuration
HF_USER=Jbutch
DATASET="record-prod25"
OUTPUT_DIR="/net/scratch/jbutch/lerobot/multi/episodes_25"
NUM_EPISODES=25

# Generate episode indices (0 to NUM_EPISODES-1)
EPISODE_INDICES=$(seq -s ',' 0 $((NUM_EPISODES - 1)))

echo "=================================================="
echo "Training with $NUM_EPISODES episodes (Single GPU, batch 16)"
echo "Output: $OUTPUT_DIR"
echo "Episodes: $EPISODE_INDICES"
echo "=================================================="

# Remove old failed output
rm -rf "$OUTPUT_DIR"

# Set environment variables
export PYTHONUNBUFFERED=1

# Use single GPU with larger batch size
CUDA_VISIBLE_DEVICES=0 lerobot-train \
    --dataset.repo_id=${HF_USER}/${DATASET} \
    --dataset.episodes="[$EPISODE_INDICES]" \
    --policy.type=act \
    --output_dir=${OUTPUT_DIR} \
    --job_name=act_so101_ep${NUM_EPISODES} \
    --policy.device=cuda \
    --wandb.enable=true \
    --batch_size=16 \
    --policy.repo_id=${HF_USER}/policy_ep${NUM_EPISODES}

echo ""
echo "Completed training with $NUM_EPISODES episodes"
echo "=================================================="
