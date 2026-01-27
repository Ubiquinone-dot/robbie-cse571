#!/usr/bin/env python3
"""Interactive motor testing for SO-101 arms (leader or follower)."""
import os
import time
from pathlib import Path

import yaml
from dotenv import load_dotenv
from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor, MotorNormMode

load_dotenv()

CONFIG_PATH = Path(__file__).parent / "config.yaml"
LEADER_PORT = os.getenv("LEADER_ARM_PORT")
FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")
MOTOR_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
MOTOR_IDS = {name: i + 1 for i, name in enumerate(MOTOR_NAMES)}


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def select_arm():
    """Prompt user to select which arm to control."""
    print("Select arm to control:")
    print(f"  1. Leader   ({LEADER_PORT})")
    print(f"  2. Follower ({FOLLOWER_PORT})")

    while True:
        choice = input("Enter choice (1/2): ").strip()
        if choice == "1":
            return "leader", LEADER_PORT
        elif choice == "2":
            return "follower", FOLLOWER_PORT
        else:
            print("Invalid choice. Enter 1 or 2.")


def main():
    # Select which arm to use
    arm_name, port = select_arm()

    print(f"\nConnecting to {arm_name} arm on {port}...")
    bus = FeetechMotorsBus(
        port=port,
        motors={
            name: Motor(id=id_, model="sts3215", norm_mode=MotorNormMode.RANGE_M100_100)
            for name, id_ in MOTOR_IDS.items()
        },
    )
    bus.connect()
    print("Connected!\n", bus)

    # Load default positions from config
    config = load_config()
    default_positions = config["default_position"][arm_name]
    print(f"Default positions for {arm_name} (from config.yaml):")
    for name in MOTOR_NAMES:
        print(f"  {name:15}: {default_positions[name]:4}")

    # Disable torque and unlock so arm moves freely
    print("\nDisabling torque and unlocking (arm will move freely)...")
    bus.sync_write("Torque_Enable", {name: 0 for name in MOTOR_NAMES}, normalize=False)
    bus.sync_write("Lock", {name: 0 for name in MOTOR_NAMES}, normalize=False)

    while True:
        print("\n" + "=" * 50)
        print(f"Controlling: {arm_name.upper()} arm")
        print("Commands:")
        print("  r      - Read all motor positions")
        print("  m      - Move a motor to position")
        print("  s      - Run sequence (move each motor back and forth)")
        print("  return - Return to default position")
        print("  relax  - Disable torque (free movement)")
        print("  hold   - Enable torque (hold position)")
        print("  q      - Quit")
        print("=" * 50)

        cmd = input("Enter command: ").strip().lower()

        if cmd == "q":
            break

        elif cmd == "r":
            positions = bus.sync_read("Present_Position", MOTOR_NAMES, normalize=False)
            print("\nMotor positions (raw values, 0-4095):")
            for name in MOTOR_NAMES:
                print(f"  {name:15} (ID {MOTOR_IDS[name]}): {positions[name]:4}")

        elif cmd == "s":
            # Sequence: move each motor back and forth
            offset = 300  # Steps to move in each direction
            delay = 0.5   # Seconds between movements

            print("\nRunning sequence - moving each motor back and forth...")
            print(f"Offset: ±{offset} steps, Delay: {delay}s\n")

            # Save current positions for this sequence
            current = bus.sync_read("Present_Position", MOTOR_NAMES, normalize=False)

            # Enable torque on all motors
            bus.sync_write("Torque_Enable", {name: 1 for name in MOTOR_NAMES}, normalize=False)

            for name in MOTOR_NAMES:
                curr_pos = current[name]
                pos_plus = min(4095, curr_pos + offset)
                pos_minus = max(0, curr_pos - offset)

                print(f"{name}: {curr_pos} -> {pos_plus} -> {pos_minus} -> {curr_pos}")

                # Move forward
                bus.sync_write("Goal_Position", {name: pos_plus}, normalize=False)
                time.sleep(delay)

                # Move backward
                bus.sync_write("Goal_Position", {name: pos_minus}, normalize=False)
                time.sleep(delay)

                # Return to current
                bus.sync_write("Goal_Position", {name: curr_pos}, normalize=False)
                time.sleep(delay)

            print("\nSequence complete! (use 'relax' to free arm)")

        elif cmd == "return":
            print("\nReturning to default position...")

            # Enable torque on all motors
            bus.sync_write("Torque_Enable", {name: 1 for name in MOTOR_NAMES}, normalize=False)

            # Move all motors to default positions
            bus.sync_write("Goal_Position", default_positions, normalize=False)

            print("Moving to:")
            for name in MOTOR_NAMES:
                print(f"  {name:15}: {default_positions[name]:4}")

            # Wait for movement to complete
            time.sleep(1.0)
            print("Done! (use 'relax' to free arm)")

        elif cmd == "relax":
            print("\nDisabling torque and unlocking all motors...")
            bus.sync_write("Torque_Enable", {name: 0 for name in MOTOR_NAMES}, normalize=False)
            bus.sync_write("Lock", {name: 0 for name in MOTOR_NAMES}, normalize=False)
            print("All motors relaxed - arm moves freely.")

        elif cmd == "hold":
            print("\nEnabling torque and locking all motors...")
            bus.sync_write("Torque_Enable", {name: 1 for name in MOTOR_NAMES}, normalize=False)
            bus.sync_write("Lock", {name: 1 for name in MOTOR_NAMES}, normalize=False)
            print("All motors holding position.")

        elif cmd == "m":
            print("\nMotors:")
            for i, name in enumerate(MOTOR_NAMES):
                print(f"  {i + 1}. {name}")

            try:
                motor_num = int(input("Select motor (1-6): ")) - 1
                if 0 <= motor_num < len(MOTOR_NAMES):
                    motor_name = MOTOR_NAMES[motor_num]
                    current_pos = bus.sync_read("Present_Position", [motor_name], normalize=False)
                    print(f"Current position: {current_pos[motor_name]}")

                    pos = int(input("Enter target position (0-4095): "))
                    if 0 <= pos <= 4095:
                        # Enable torque for this motor
                        bus.sync_write("Torque_Enable", {motor_name: 1}, normalize=False)
                        bus.sync_write("Goal_Position", {motor_name: pos}, normalize=False)
                        print(f"Moving {motor_name} to {pos}")
                    else:
                        print("Position must be 0-4095")
                else:
                    print("Invalid motor number")
            except ValueError:
                print("Invalid input")

    print("\nDisabling torque and disconnecting...")
    bus.sync_write("Torque_Enable", {name: 0 for name in MOTOR_NAMES}, normalize=False)
    bus.disconnect()
    print("Done!")


if __name__ == "__main__":
    main()
