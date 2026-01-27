#!/usr/bin/env python3
"""Monitor motor voltage, temperature, current, and load."""
import os
import time
from dotenv import load_dotenv
from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor, MotorNormMode

load_dotenv()

LEADER_PORT = os.getenv("LEADER_ARM_PORT")
FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")
MOTOR_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
MOTOR_IDS = {name: i + 1 for i, name in enumerate(MOTOR_NAMES)}


def create_bus(port):
    return FeetechMotorsBus(
        port=port,
        motors={
            name: Motor(id=id_, model="sts3215", norm_mode=MotorNormMode.RANGE_M100_100)
            for name, id_ in MOTOR_IDS.items()
        },
    )


def monitor(bus, arm_name, interval=0.5):
    """Continuously monitor motor stats."""
    print(f"\nMonitoring {arm_name} arm (Ctrl+C to stop)\n")
    print("Voltage is reported in 0.1V units (e.g., 75 = 7.5V)")
    print("Temperature is in Celsius")
    print("-" * 70)

    try:
        while True:
            voltage = bus.sync_read("Present_Voltage", normalize=False)
            temp = bus.sync_read("Present_Temperature", normalize=False)
            load = bus.sync_read("Present_Load", normalize=False)
            current = bus.sync_read("Present_Current", normalize=False)

            # Clear screen and print header
            print("\033[2J\033[H")  # Clear screen
            print(f"=== {arm_name.upper()} ARM MONITOR === (Ctrl+C to stop)")
            print(f"{'Motor':<15} | {'Volt':>6} | {'Temp':>6} | {'Load':>6} | {'Current':>7}")
            print("-" * 55)

            min_voltage = 255
            max_temp = 0

            for name in MOTOR_NAMES:
                v = voltage[name]
                t = temp[name]
                l = load[name]
                c = current[name]
                min_voltage = min(min_voltage, v)
                max_temp = max(max_temp, t)

                # Voltage warning
                v_str = f"{v/10:.1f}V"
                if v < 60:  # Below 6V is danger zone
                    v_str += " LOW!"

                print(f"{name:<15} | {v_str:>6} | {t:>4}°C | {l:>6} | {c:>7}")

            print("-" * 55)
            print(f"{'SUMMARY':<15} | {min_voltage/10:.1f}V min | {max_temp}°C max")

            if min_voltage < 60:
                print("\n*** WARNING: Voltage below 6V - motors may brown out! ***")
            elif min_voltage < 65:
                print("\n* Caution: Voltage getting low")

            time.sleep(interval)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")


def main():
    print("Select arm to monitor:")
    print(f"  1. Leader   ({LEADER_PORT})")
    print(f"  2. Follower ({FOLLOWER_PORT})")
    print(f"  3. Both (alternating)")

    choice = input("Enter choice (1/2/3): ").strip()

    if choice == "1":
        bus = create_bus(LEADER_PORT)
        bus.connect()
        monitor(bus, "leader")
        bus.disconnect()
    elif choice == "2":
        bus = create_bus(FOLLOWER_PORT)
        bus.connect()
        monitor(bus, "follower")
        bus.disconnect()
    elif choice == "3":
        leader_bus = create_bus(LEADER_PORT)
        follower_bus = create_bus(FOLLOWER_PORT)
        leader_bus.connect()
        follower_bus.connect()

        try:
            while True:
                for bus, name in [(leader_bus, "leader"), (follower_bus, "follower")]:
                    voltage = bus.sync_read("Present_Voltage", normalize=False)
                    temp = bus.sync_read("Present_Temperature", normalize=False)

                    min_v = min(voltage.values()) / 10
                    max_t = max(temp.values())

                    status = ""
                    if min_v < 6.0:
                        status = " ** LOW VOLTAGE **"
                    print(f"{name:8}: {min_v:.1f}V min, {max_t}°C max{status}")

                print("-" * 40)
                time.sleep(1)

        except KeyboardInterrupt:
            print("\nStopped.")

        leader_bus.disconnect()
        follower_bus.disconnect()
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()
