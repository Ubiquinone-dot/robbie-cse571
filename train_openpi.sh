#!/bin/bash
#SBATCH --job-name=pi05_so101
#SBATCH --output=/net/scratch/jbutch/lerobot/pi05_p2/slurm-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/pi05_p2/slurm-%j.err
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

# Configuration
DATASET_REPO="hangyufeng/record-project2"
POLICY_USER="Jbutch"
BASE_DIR="/net/scratch/jbutch/lerobot/pi05_p2"
CHECKPOINT_MODEL="${BASE_DIR}/run/checkpoints/last/pretrained_model"
OUTPUT_DIR="${BASE_DIR}/run2"

# Ensure base directory exists (for SLURM logs)
mkdir -p "$BASE_DIR"

# Pre-download the dataset and model before launching multi-GPU
echo "Pre-downloading dataset..."
python -c "
from lerobot.datasets.lerobot_dataset import LeRobotDataset
print('Downloading dataset...')
ds = LeRobotDataset('${DATASET_REPO}')
print(f'Dataset loaded: {len(ds)} samples')
print('Pre-download complete.')
"

echo "=================================================="
echo "Pi0.5 VLA Continued Fine-tuning (8x L40 GPU)"
echo "=================================================="
echo "Dataset:       $DATASET_REPO"
echo "Policy:        pi05"
echo "Pretrained:    $CHECKPOINT_MODEL (from step 3000)"
echo "Output:        $OUTPUT_DIR"
echo "=================================================="

# Remove old output to avoid FileExistsError
rm -rf "$OUTPUT_DIR"

accelerate launch \
    --config_file accelerate_config.yaml \
    train_pi05_wrapper.py \
    --dataset.repo_id=${DATASET_REPO} \
    --policy.type=pi05 \
    --policy.pretrained_path=${CHECKPOINT_MODEL} \
    --policy.compile_model=false \
    --policy.gradient_checkpointing=true \
    --policy.dtype=bfloat16 \
    --policy.freeze_vision_encoder=true \
    --policy.train_expert_only=true \
    --output_dir=${OUTPUT_DIR} \
    --job_name=pi05_so101_cont \
    --policy.device=cuda \
    --batch_size=16 \
    --steps=3000 \
    --wandb.enable=true \
    --policy.repo_id=${POLICY_USER}/pi05_p2_6k

echo ""
echo "=================================================="
echo "Pi0.5 continued training completed!"
echo "=================================================="
