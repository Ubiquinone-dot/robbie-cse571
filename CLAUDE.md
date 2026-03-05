# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

R.O.B.B.I.E. (Robot Operation By Behavioral Imitation Engine) - SO-101 dual-arm teleoperation and imitation learning using the LeRobot library. The system supports data collection via teleoperation, ACT policy training on SLURM clusters, and inference on macOS with MPS.

## Commands

```bash
# Install dependencies
uv sync

# Hardware control (requires physical robot connected via USB)
uv run python calibrate.py       # Calibrate arms (run once after setup)
uv run python teleoperate.py     # Leader→follower real-time mirroring
uv run python test_motors.py     # Interactive motor testing CLI
uv run python monitor.py         # Motor diagnostics (voltage/temp/load)
uv run python relax.py           # Disable torque (free movement)
uv run python reset.py           # Reset follower to home position

# Data collection
./gather.sh                                       # Record demos (default: 5 episodes)
NUM_EPISODES=20 DATASET=my_data ./gather.sh       # Custom episode count/dataset

# Training (SLURM cluster)
sbatch train.sh                                   # Submit training job
DATASET=my_data sbatch train.sh                   # Train on custom dataset

# Inference (macOS)
uv run python inference.py ep25                   # Run with HF policy (ep5, ep10, ep25)
uv run python inference.py multi_p2_8gpu_ep48     # Run with local checkpoint
uv run python inference.py ep25 10                # 10 episodes
./inference.sh ep25 "pick up the black cube" 5    # Shell wrapper with auto-reset

# Analysis & debugging
uv run python debug_policy.py      # Inspect policy outputs/tensor shapes
uv run python analyze_dataset.py   # Check dataset consistency
uv run python plot_variance.py     # Plot demonstration variance
uv run python camera_web/app.py    # Web dashboard with camera + motor telemetry
```

## Architecture

### Pipeline: Collect → Train → Evaluate

1. **Data collection** (`gather.sh`): Leader arm teleoperation recorded via `lerobot-record` with front camera (640x480 @ 30fps, 15s episodes). Pushes to HuggingFace Hub as `Jbutch/<dataset_name>`.

2. **Training** (`train.sh`): SLURM job (1x L40 GPU, 8 CPUs, 64GB RAM, ~24h). Trains ACT (Action Chunking Transformers) policy via `lerobot-train`. Logs to WandB. Outputs to `outputs/train/`.

3. **Inference** (`inference.py`): Loads ACT policy (from HF Hub or `checkpoints/` dir), runs on follower arm with camera, records evaluation episodes. Device: MPS on macOS.

### Motor Control

Uses `FeetechMotorsBus` (sts3215 servos) with 6 motors per arm: `shoulder_pan`, `shoulder_lift`, `elbow_flex`, `wrist_flex`, `wrist_roll`, `gripper` (IDs 1-6, range 0-4095).

- Leader: `SO101Leader` from `lerobot.teleoperators.so_leader`
- Follower: `SO101Follower` from `lerobot.robots.so_follower`

```python
bus.sync_read("Present_Position", MOTOR_NAMES, normalize=False)
bus.sync_write("Goal_Position", {motor_name: position}, normalize=False)
bus.sync_write("Torque_Enable", {name: 0 for name in MOTOR_NAMES}, normalize=False)
```

### Configuration

- `.env` - `LEADER_ARM_PORT`, `FOLLOWER_ARM_PORT`, `HF_REPO_ID` (find ports with `ls /dev/tty.usbmodem*`)
- `config.yaml` - Default motor positions per arm (used by `reset.py`)
- `checkpoints/` - Model weights stored via Git LFS (`.safetensors` files, ~200MB each)

### Web Dashboard (`camera_web/app.py`)

Flask app with MJPEG camera stream, real-time motor telemetry for both arms, and reconnect capability. Polls at 200ms intervals.
