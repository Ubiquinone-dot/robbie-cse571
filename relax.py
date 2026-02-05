#!/usr/bin/env python3
"""Relax all motors on SO-101 arms (disable torque and lock)."""
import os
import sys

from dotenv import load_dotenv

from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor, MotorNormMode

load_dotenv()

LEADER_PORT = os.getenv("LEADER_ARM_PORT")
FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")
MOTOR_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
MOTOR_IDS = {name: i + 1 for i, name in enumerate(MOTOR_NAMES)}


def relax_arm(port: str, name: str) -> bool:
    """Relax a single arm by disabling torque and lock."""
    if not port:
        print(f"  {name}: skipped (no port configured)")
        return False

    try:
        bus = FeetechMotorsBus(
            port=port,
            motors={
                motor_name: Motor(id=id_, model="sts3215", norm_mode=MotorNormMode.RANGE_M100_100)
                for motor_name, id_ in MOTOR_IDS.items()
            },
        )
        bus.connect()
        bus.sync_write("Torque_Enable", {n: 0 for n in MOTOR_NAMES}, normalize=False)
        bus.sync_write("Lock", {n: 0 for n in MOTOR_NAMES}, normalize=False)
        bus.disconnect()
        print(f"  {name}: relaxed")
        return True
    except Exception as e:
        print(f"  {name}: failed ({e})")
        return False


def main():
    arms = sys.argv[1:] if len(sys.argv) > 1 else ["leader", "follower"]

    print("Relaxing arms...")
    for arm in arms:
        if arm == "leader":
            relax_arm(LEADER_PORT, "leader")
        elif arm == "follower":
            relax_arm(FOLLOWER_PORT, "follower")
        else:
            print(f"  {arm}: unknown arm")


if __name__ == "__main__":
    main()
