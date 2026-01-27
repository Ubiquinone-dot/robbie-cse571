#!/usr/bin/env python3
import os
from dotenv import load_dotenv

from lerobot.teleoperators.so_leader import SO101LeaderConfig, SO101Leader
from lerobot.robots.so_follower import SO101FollowerConfig, SO101Follower

load_dotenv()

LEADER_PORT = os.getenv("LEADER_ARM_PORT")
FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")


def calibrate_leader():
    print(f"Calibrating leader arm on {LEADER_PORT}...")
    config = SO101LeaderConfig(port=LEADER_PORT, id="leader_arm")
    leader = SO101Leader(config)
    leader.connect(calibrate=False)
    leader.calibrate()
    leader.disconnect()
    print("Leader arm calibration complete.")


def calibrate_follower():
    print(f"Calibrating follower arm on {FOLLOWER_PORT}...")
    config = SO101FollowerConfig(port=FOLLOWER_PORT, id="follower_arm")
    follower = SO101Follower(config)
    follower.connect(calibrate=False)
    follower.calibrate()
    follower.disconnect()
    print("Follower arm calibration complete.")


if __name__ == "__main__":
    if LEADER_PORT:
        calibrate_leader()
    if FOLLOWER_PORT:
        calibrate_follower()