#!/bin/bash
#SBATCH --job-name=act_basket_1gpu
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
export NCCL_DEBUG=INFO
export NCCL_DEBUG_SUBSYS=ALL

# Configuration
DATASET_REPO="hangyufeng/place_the_basket"
POLICY_USER="Jbutch"
OUTPUT_DIR="/net/scratch/jbutch/lerobot/act_basket/run_2gpu"

# Generate episode indices (0 to 49, dataset has 50 episodes)
EPISODE_INDICES=$(seq -s ',' 0 49)

echo "=================================================="
echo "LeRobot ACT Training - place_the_basket (2x L40)"
echo "=================================================="

# Remove old output to avoid FileExistsError
rm -rf "$OUTPUT_DIR"

accelerate launch \
    --multi_gpu \
    --num_processes=2 \
    --main_process_port=29501 \
    $(which lerobot-train) \
    --dataset.repo_id=${DATASET_REPO} \
    --dataset.episodes="[$EPISODE_INDICES]" \
    --policy.type=act \
    --output_dir=${OUTPUT_DIR} \
    --job_name=act_basket_2gpu \
    --policy.device=cuda \
    --wandb.enable=true \
    --policy.repo_id=${POLICY_USER}/act_place_basket

echo "ACT 1GPU training completed!"
