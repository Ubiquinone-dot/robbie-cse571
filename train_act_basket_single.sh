#!/bin/bash
#SBATCH --job-name=act_basket_s
#SBATCH --output=/net/scratch/jbutch/lerobot/act_basket/slurm-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/act_basket/slurm-%j.err
#SBATCH --partition=gpu-train
#SBATCH --gres=gpu:l40:2
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=72:00:00

# Change to project directory (needed for SLURM)
cd /home/jbutch/Projects/MT25/robbie-cse571

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export PYTHONUNBUFFERED=1
export CUDA_VISIBLE_DEVICES=0

# Configuration
DATASET_REPO="hangyufeng/place_the_basket"
POLICY_USER="Jbutch"
OUTPUT_DIR="/net/scratch/jbutch/lerobot/act_basket/run_single"

# Generate episode indices (0 to 49, dataset has 50 episodes)
EPISODE_INDICES=$(seq -s ',' 0 49)

echo "=================================================="
echo "LeRobot ACT Training - place_the_basket (1x L40, single process)"
echo "=================================================="

# Remove old output to avoid FileExistsError
rm -rf "$OUTPUT_DIR"

lerobot-train \
    --dataset.repo_id=${DATASET_REPO} \
    --dataset.episodes="[$EPISODE_INDICES]" \
    --policy.type=act \
    --output_dir=${OUTPUT_DIR} \
    --job_name=act_basket_single \
    --policy.device=cuda \
    --wandb.enable=true \
    --policy.repo_id=${POLICY_USER}/act_place_basket

echo "ACT single-GPU training completed!"
