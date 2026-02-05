#!/usr/bin/env python3
"""Reset follower arm to the home position."""
import os
import time

from dotenv import load_dotenv

from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor, MotorNormMode

load_dotenv()

FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")
MOTOR_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
MOTOR_IDS = {name: i + 1 for i, name in enumerate(MOTOR_NAMES)}

HOME_POSITION = {
    "shoulder_pan": 2034,
    "shoulder_lift": 719,
    "elbow_flex": 3135,
    "wrist_flex": 2728,
    "wrist_roll": 2049,
    "gripper": 2047,
}


def main():
    if not FOLLOWER_PORT:
        print("Error: FOLLOWER_ARM_PORT not configured in .env")
        return

    print(f"Connecting to follower ({FOLLOWER_PORT})...")
    bus = FeetechMotorsBus(
        port=FOLLOWER_PORT,
        motors={
            name: Motor(id=id_, model="sts3215", norm_mode=MotorNormMode.RANGE_M100_100)
            for name, id_ in MOTOR_IDS.items()
        },
    )
    bus.connect()

    print("Moving to home position...")
    bus.sync_write("Torque_Enable", {name: 1 for name in MOTOR_NAMES}, normalize=False)
    bus.sync_write("Goal_Position", HOME_POSITION, normalize=False)
    time.sleep(1.0)

    print("Home position:")
    for name in MOTOR_NAMES:
        print(f"  {name}: {HOME_POSITION[name]}")

    bus.disconnect()


if __name__ == "__main__":
    main()
