# R.O.B.B.I.E.
**Robot Operation By Behavioral Imitation Engine**

SO-101 dual-arm teleoperation and control.

## Setup

### Install uv (if needed)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Git LFS (for model checkpoints)
```bash
brew install git-lfs
git lfs install
```

### Install dependencies
```bash
uv sync
```

### Configure ports
Create a `.env` file with your arm ports:
```bash
LEADER_ARM_PORT=/dev/tty.usbmodem58760431551
FOLLOWER_ARM_PORT=/dev/tty.usbmodem58760431541
```

Find ports with:
```bash
ls /dev/tty.usbmodem*
```

## Scripts

### calibrate.py
Calibrate leader and/or follower arms. Run this first.
```bash
uv run python calibrate.py
```

### teleoperate.py
Control the follower arm by moving the leader arm.
```bash
uv run python teleoperate.py
```
Press `Ctrl+C` to stop.

### test_motors.py
Interactive motor testing and diagnostics.
```bash
uv run python test_motors.py
```

Commands:
| Key | Action |
|-----|--------|
| `r` | Read motor positions |
| `m` | Move single motor |
| `s` | Run test sequence |
| `return` | Go to default position |
| `relax` | Disable torque (free movement) |
| `hold` | Enable torque (lock position) |
| `q` | Quit |

## Configuration

### config.yaml
Default positions for each arm:
```yaml
default_position:
  leader:
    shoulder_pan: 2048
    shoulder_lift: 2048
    elbow_flex: 2048
    wrist_flex: 2048
    wrist_roll: 2048
    gripper: 2048
  follower:
    shoulder_pan: 2048
    shoulder_lift: 2048
    elbow_flex: 2048
    wrist_flex: 2048
    wrist_roll: 2048
    gripper: 2048
```

Use `test_motors.py` → `r` to read current positions, then update the config.
