#!/bin/bash
# Master script to submit 3 training jobs for episode comparison
# Each job trains on a different number of episodes: 5, 10, and 25 (full)
#
# Jobs are submitted with dependencies to avoid NCCL conflicts when
# multiple accelerate jobs run on the same node.

# Configuration
HF_USER=Jbutch
DATASET="record-prod25"
BASE_OUTPUT_DIR="/net/scratch/jbutch/lerobot/episode_comparison"

# Create base directory for SLURM logs
mkdir -p "$BASE_OUTPUT_DIR"

echo "=================================================="
echo "Submitting Episode Comparison Training Jobs"
echo "=================================================="
echo "Dataset:       $HF_USER/$DATASET"
echo "Policy:        act"
echo "Base Output:   $BASE_OUTPUT_DIR"
echo "=================================================="

# Submit job for 5 episodes
echo "Submitting 5-episode training job..."
JOB1=$(sbatch --parsable <<'SLURM_SCRIPT'
#!/bin/bash
#SBATCH --job-name=act_5_episodes
#SBATCH --partition=gpu-train
#SBATCH --output=/net/scratch/jbutch/lerobot/episode_comparison/slurm-5ep-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/episode_comparison/slurm-5ep-%j.err
#SBATCH --gres=gpu:l40:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=23:59:00

cd /home/jbutch/Projects/MT25/robbie-cse571
source .venv/bin/activate

echo "Training ACT policy on 5 episodes"
accelerate launch \
    --multi_gpu \
    --num_processes=2 \
    $(which lerobot-train) \
    --dataset.repo_id=Jbutch/record-prod25 \
    --dataset.episodes='[0,1,2,3,4]' \
    --policy.type=act \
    --output_dir=/net/scratch/jbutch/lerobot/episode_comparison/5_episodes \
    --job_name=act_5_episodes \
    --policy.device=cuda \
    --wandb.enable=true \
    --policy.repo_id=Jbutch/act_5_episodes
SLURM_SCRIPT
)
echo "  Submitted job $JOB1 (5 episodes)"

# Submit job for 10 episodes (depends on 5-episode job)
echo "Submitting 10-episode training job (depends on $JOB1)..."
JOB2=$(sbatch --parsable --dependency=afterany:$JOB1 <<'SLURM_SCRIPT'
#!/bin/bash
#SBATCH --job-name=act_10_episodes
#SBATCH --partition=gpu-train
#SBATCH --output=/net/scratch/jbutch/lerobot/episode_comparison/slurm-10ep-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/episode_comparison/slurm-10ep-%j.err
#SBATCH --gres=gpu:l40:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=23:59:00

cd /home/jbutch/Projects/MT25/robbie-cse571
source .venv/bin/activate

echo "Training ACT policy on 10 episodes"
accelerate launch \
    --multi_gpu \
    --num_processes=2 \
    $(which lerobot-train) \
    --dataset.repo_id=Jbutch/record-prod25 \
    --dataset.episodes='[0,1,2,3,4,5,6,7,8,9]' \
    --policy.type=act \
    --output_dir=/net/scratch/jbutch/lerobot/episode_comparison/10_episodes \
    --job_name=act_10_episodes \
    --policy.device=cuda \
    --wandb.enable=true \
    --policy.repo_id=Jbutch/act_10_episodes
SLURM_SCRIPT
)
echo "  Submitted job $JOB2 (10 episodes)"

# Submit job for 25 episodes (depends on 10-episode job)
echo "Submitting 25-episode training job (depends on $JOB2)..."
JOB3=$(sbatch --parsable --dependency=afterany:$JOB2 <<'SLURM_SCRIPT'
#!/bin/bash
#SBATCH --job-name=act_25_episodes
#SBATCH --partition=gpu-train
#SBATCH --output=/net/scratch/jbutch/lerobot/episode_comparison/slurm-25ep-%j.out
#SBATCH --error=/net/scratch/jbutch/lerobot/episode_comparison/slurm-25ep-%j.err
#SBATCH --gres=gpu:l40:2
#SBATCH --cpus-per-task=16
#SBATCH --mem=128G
#SBATCH --time=23:59:00

cd /home/jbutch/Projects/MT25/robbie-cse571
source .venv/bin/activate

echo "Training ACT policy on 25 episodes (full dataset)"
accelerate launch \
    --multi_gpu \
    --num_processes=2 \
    $(which lerobot-train) \
    --dataset.repo_id=Jbutch/record-prod25 \
    --policy.type=act \
    --output_dir=/net/scratch/jbutch/lerobot/episode_comparison/25_episodes \
    --job_name=act_25_episodes \
    --policy.device=cuda \
    --wandb.enable=true \
    --policy.repo_id=Jbutch/act_25_episodes
SLURM_SCRIPT
)
echo "  Submitted job $JOB3 (25 episodes)"

echo ""
echo "=================================================="
echo "All jobs submitted!"
echo "Job chain: $JOB1 -> $JOB2 -> $JOB3"
echo "Monitor with: squeue -u $USER"
echo "=================================================="
