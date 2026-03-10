#!/bin/bash
#SBATCH --job-name=pi05_debug
#SBATCH --output=/net/scratch/jbutch/lerobot/pi05_p2_debug/slurm-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/pi05_p2_debug/slurm-%j.err
#SBATCH --partition=gpu
#SBATCH --gres=gpu:a6000:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=24:00:00

# Change to project directory (needed for SLURM)
cd /home/jbutch/Projects/MT25/robbie-cse571

# Activate virtual environment
source .venv/bin/activate

# Set environment variables
export PYTHONUNBUFFERED=1

# Configuration
DATASET_REPO="hangyufeng/record-project2"
POLICY_USER="Jbutch"
BASE_DIR="/net/scratch/jbutch/lerobot/pi05_p2_debug"
OUTPUT_DIR="${BASE_DIR}/run"

# Ensure base directory exists (for SLURM logs)
mkdir -p "$BASE_DIR"

echo "=================================================="
echo "Pi0.5 VLA Fine-tuning (1x A6000 GPU - debug)"
echo "=================================================="
echo "Dataset:       $DATASET_REPO"
echo "Policy:        pi05"
echo "Pretrained:    lerobot/pi05_base"
echo "Output:        $OUTPUT_DIR"
echo "=================================================="

# Remove old output to avoid FileExistsError
rm -rf "$OUTPUT_DIR"

lerobot-train \
    --dataset.repo_id=${DATASET_REPO} \
    --policy.type=pi05 \
    --policy.pretrained_path=lerobot/pi05_base \
    --policy.compile_model=true \
    --policy.gradient_checkpointing=true \
    --policy.dtype=bfloat16 \
    --policy.freeze_vision_encoder=false \
    --policy.train_expert_only=false \
    --output_dir=${OUTPUT_DIR} \
    --job_name=pi05_debug \
    --policy.device=cuda \
    --batch_size=4 \
    --steps=3000 \
    --wandb.enable=true \
    --policy.repo_id=${POLICY_USER}/pi05_p2_debug

echo ""
echo "=================================================="
echo "Pi0.5 debug training completed!"
echo "=================================================="
