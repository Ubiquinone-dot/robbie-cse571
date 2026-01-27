#!/usr/bin/env python3
"""Teleoperate the follower arm using the leader arm."""
import os

from dotenv import load_dotenv
from lerobot.teleoperators.so_leader import SO101LeaderConfig, SO101Leader
from lerobot.robots.so_follower import SO101FollowerConfig, SO101Follower

load_dotenv()

LEADER_PORT = os.getenv("LEADER_ARM_PORT")
FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")


def main():
    print(f"Leader arm:   {LEADER_PORT}")
    print(f"Follower arm: {FOLLOWER_PORT}")

    robot_config = SO101FollowerConfig(
        port=FOLLOWER_PORT,
        id="follower_arm",
    )

    teleop_config = SO101LeaderConfig(
        port=LEADER_PORT,
        id="leader_arm",
    )

    robot = SO101Follower(robot_config)
    teleop_device = SO101Leader(teleop_config)

    print("\nConnecting to follower...")
    robot.connect()
    print("Connecting to leader...")
    teleop_device.connect()

    print("\nTeleoperation active! Move the leader arm to control the follower.")
    print("Press Ctrl+C to stop.\n")

    try:
        while True:
            action = teleop_device.get_action()
            robot.send_action(action)
    except KeyboardInterrupt:
        print("\n\nStopping teleoperation...")
    finally:
        teleop_device.disconnect()
        robot.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()
