#!/bin/bash
#SBATCH --job-name=smolvla_basket_1gpu
#SBATCH --output=/net/scratch/jbutch/lerobot/smolvla_basket/slurm-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/smolvla_basket/slurm-%j.err
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
OUTPUT_DIR="/net/scratch/jbutch/lerobot/smolvla_basket/run_2gpu"

# Generate episode indices (0 to 49, dataset has 50 episodes)
EPISODE_INDICES=$(seq -s ',' 0 49)

echo "=================================================="
echo "LeRobot SmolVLA Training - place_the_basket (2x L40)"
echo "=================================================="

# Remove old output to avoid FileExistsError
rm -rf "$OUTPUT_DIR"

accelerate launch \
    --multi_gpu \
    --num_processes=2 \
    $(which lerobot-train) \
    --dataset.repo_id=${DATASET_REPO} \
    --dataset.episodes="[$EPISODE_INDICES]" \
    --policy.path=lerobot/smolvla_base \
    --output_dir=${OUTPUT_DIR} \
    --job_name=smolvla_basket_2gpu \
    --policy.device=cuda \
    --batch_size=4 \
    --wandb.enable=true \
    --policy.use_amp=true \
    --policy.repo_id=${POLICY_USER}/smolvla_place_basket

echo "SmolVLA 1GPU training completed!"
