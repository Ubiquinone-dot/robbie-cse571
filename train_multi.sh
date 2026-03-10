#!/bin/bash
#SBATCH --job-name=act_so101_multi
#SBATCH --output=/net/scratch/jbutch/lerobot/multi_p2_8gpu/slurm-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/multi_p2_8gpu/slurm-%j.err
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
BASE_OUTPUT_DIR="/net/scratch/jbutch/lerobot/multi_p2_8gpu"

# Episode counts to train on (dataset has 48 episodes)
EPISODE_COUNTS=(48 25 10)

# Ensure base output directory exists
mkdir -p "$BASE_OUTPUT_DIR"

echo "=================================================="
echo "LeRobot Multi-Episode Training (8x L40 GPU)"
echo "=================================================="
echo "Dataset:       $DATASET_REPO"
echo "Policy:        act"
echo "Base Output:   $BASE_OUTPUT_DIR"
echo "Episode Sets:  ${EPISODE_COUNTS[*]}"
echo "=================================================="

for NUM_EPISODES in "${EPISODE_COUNTS[@]}"; do
    OUTPUT_DIR="${BASE_OUTPUT_DIR}/episodes_${NUM_EPISODES}"

    # Generate episode indices (0 to NUM_EPISODES-1)
    EPISODE_INDICES=$(seq -s ',' 0 $((NUM_EPISODES - 1)))

    # Remove old output to avoid FileExistsError
    rm -rf "$OUTPUT_DIR"

    echo ""
    echo "=================================================="
    echo "Training with $NUM_EPISODES episodes"
    echo "Output: $OUTPUT_DIR"
    echo "Episodes: $EPISODE_INDICES"
    echo "=================================================="

    accelerate launch \
        --multi_gpu \
        --num_processes=8 \
        $(which lerobot-train) \
        --dataset.repo_id=${DATASET_REPO} \
        --dataset.episodes="[$EPISODE_INDICES]" \
        --policy.type=act \
        --output_dir=${OUTPUT_DIR} \
        --job_name=act_so101_ep${NUM_EPISODES} \
        --policy.device=cuda \
        --wandb.enable=true \
        --policy.repo_id=${POLICY_USER}/act_p2_ep${NUM_EPISODES}

    echo ""
    echo "Completed training with $NUM_EPISODES episodes"
    echo "=================================================="
done

echo ""
echo "=================================================="
echo "All training runs completed!"
echo "=================================================="
