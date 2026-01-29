# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

R.O.B.B.I.E. (Robot Operation By Behavioral Imitation Engine) - SO-101 dual-arm teleoperation and control using the LeRobot library.

## Commands

```bash
# Install dependencies
uv sync

# Run scripts
uv run python calibrate.py    # Calibrate arms (run first)
uv run python teleoperate.py  # Control follower via leader arm
uv run python test_motors.py  # Interactive motor testing
uv run python monitor.py      # Monitor voltage/temp/load
uv run python camera_web/app.py  # Web dashboard with camera feed
```

## Architecture

**Core scripts** (project root):
- `calibrate.py` - Arm calibration using LeRobot's SO101Leader/SO101Follower
- `teleoperate.py` - Real-time leader→follower mirroring loop
- `test_motors.py` - Interactive motor control via FeetechMotorsBus
- `monitor.py` - Motor diagnostics (voltage, temperature, load, current)

**Web dashboard** (`camera_web/`):
- Flask app with live camera feed and robot state display
- Polls motor data at 200ms intervals

**Configuration**:
- `.env` - Arm ports (`LEADER_ARM_PORT`, `FOLLOWER_ARM_PORT`)
- `config.yaml` - Default motor positions (0-4095 range per motor)

## Key Patterns

**Motor control**: Uses `FeetechMotorsBus` with 6 motors per arm:
- Motor names: `shoulder_pan`, `shoulder_lift`, `elbow_flex`, `wrist_flex`, `wrist_roll`, `gripper`
- Motor IDs: 1-6 (sequential)
- Position range: 0-4095

**Arm abstraction**:
- Leader: `SO101Leader` from `lerobot.teleoperators.so_leader`
- Follower: `SO101Follower` from `lerobot.robots.so_follower`

**Motor bus operations**:
```python
bus.sync_read("Present_Position", MOTOR_NAMES, normalize=False)
bus.sync_write("Goal_Position", {motor_name: position}, normalize=False)
bus.sync_write("Torque_Enable", {name: 0 for name in MOTOR_NAMES}, normalize=False)
```
