#!/bin/bash
#SBATCH --job-name=act_so101_test
#SBATCH --output=outputs/train/slurm-%j.out
#SBATCH --error=outputs/train/slurm-%j.err
#SBATCH --gres=gpu:1
#SBATCH --time=24:00:00

# Activate virtual environment
source .venv/bin/activate

# Configuration (matching gather.sh)
HF_USER=Jbutch
DATASET="${DATASET:-record-prod}"

echo "=================================================="
echo "LeRobot Training"
echo "=================================================="
echo "Dataset:       $HF_USER/$DATASET"
echo "Policy:        act"
echo "Output:        outputs/train/act_so101_test"
echo "=================================================="

lerobot-train \
    --dataset.repo_id=${HF_USER}/${DATASET} \
    --policy.type=act \
    --output_dir=outputs/train/act_so101_test \
    --job_name=act_so101_test \
    --policy.device=mps \
    --wandb.enable=true \
    --policy.repo_id=${HF_USER}/my_policy
