#!/usr/bin/env python3
"""Interactive motor testing for SO-101 arms."""
import os
import time
from pathlib import Path

import yaml
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.panel import Panel

from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor, MotorNormMode

load_dotenv()

console = Console()
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
    console.print("\n[bold]Select arm:[/bold]")
    console.print(f"  [cyan]1[/cyan] Leader   [dim]({LEADER_PORT})[/dim]")
    console.print(f"  [cyan]2[/cyan] Follower [dim]({FOLLOWER_PORT})[/dim]")

    while True:
        choice = Prompt.ask("Choice", choices=["1", "2"])
        if choice == "1":
            return "leader", LEADER_PORT
        return "follower", FOLLOWER_PORT


def show_positions(bus, title="Motor Positions"):
    """Display motor positions in a table."""
    positions = bus.sync_read("Present_Position", MOTOR_NAMES, normalize=False)
    table = Table(title=title, show_header=True)
    table.add_column("Motor", style="cyan")
    table.add_column("ID", justify="center")
    table.add_column("Position", justify="right", style="green")
    for name in MOTOR_NAMES:
        table.add_row(name, str(MOTOR_IDS[name]), str(positions[name]))
    console.print(table)
    return positions


def main():
    arm_name, port = select_arm()

    with console.status(f"[bold]Connecting to {arm_name} arm..."):
        bus = FeetechMotorsBus(
            port=port,
            motors={
                name: Motor(id=id_, model="sts3215", norm_mode=MotorNormMode.RANGE_M100_100)
                for name, id_ in MOTOR_IDS.items()
            },
        )
        bus.connect()

    console.print(f"[green]Connected to {arm_name} arm[/green]")

    config = load_config()
    default_positions = config["default_position"][arm_name]

    # Relax arm on start
    bus.sync_write("Torque_Enable", {name: 0 for name in MOTOR_NAMES}, normalize=False)
    bus.sync_write("Lock", {name: 0 for name in MOTOR_NAMES}, normalize=False)
    console.print("[dim]Arm relaxed[/dim]\n")

    menu = """[bold cyan]r[/bold cyan] read   [bold cyan]m[/bold cyan] move   [bold cyan]s[/bold cyan] sequence   [bold cyan]return[/bold cyan] default
[bold cyan]relax[/bold cyan] free   [bold cyan]hold[/bold cyan] lock   [bold cyan]q[/bold cyan] quit"""

    while True:
        console.print(Panel(menu, title=f"[bold]{arm_name.upper()}[/bold]", border_style="blue"))
        cmd = Prompt.ask("[bold]>[/bold]").strip().lower()

        if cmd == "q":
            break

        elif cmd == "r":
            show_positions(bus)

        elif cmd == "s":
            offset, delay = 300, 0.5
            console.print(f"[dim]Sequence: ±{offset} steps, {delay}s delay[/dim]")
            current = bus.sync_read("Present_Position", MOTOR_NAMES, normalize=False)
            bus.sync_write("Torque_Enable", {name: 1 for name in MOTOR_NAMES}, normalize=False)

            for name in MOTOR_NAMES:
                pos = current[name]
                console.print(f"  [cyan]{name}[/cyan]", end=" ")
                for target in [min(4095, pos + offset), max(0, pos - offset), pos]:
                    bus.sync_write("Goal_Position", {name: target}, normalize=False)
                    time.sleep(delay)
                console.print("[green]✓[/green]")

            console.print("[green]Sequence complete[/green]")

        elif cmd == "return":
            with console.status("[bold]Moving to default position..."):
                bus.sync_write("Torque_Enable", {name: 1 for name in MOTOR_NAMES}, normalize=False)
                bus.sync_write("Goal_Position", default_positions, normalize=False)
                time.sleep(1.0)
            console.print("[green]At default position[/green]")

        elif cmd == "relax":
            bus.sync_write("Torque_Enable", {name: 0 for name in MOTOR_NAMES}, normalize=False)
            bus.sync_write("Lock", {name: 0 for name in MOTOR_NAMES}, normalize=False)
            console.print("[green]Relaxed[/green]")

        elif cmd == "hold":
            bus.sync_write("Torque_Enable", {name: 1 for name in MOTOR_NAMES}, normalize=False)
            bus.sync_write("Lock", {name: 1 for name in MOTOR_NAMES}, normalize=False)
            console.print("[green]Holding[/green]")

        elif cmd == "m":
            table = Table(show_header=False, box=None)
            for i, name in enumerate(MOTOR_NAMES):
                table.add_row(f"[cyan]{i+1}[/cyan]", name)
            console.print(table)

            try:
                motor_num = IntPrompt.ask("Motor", default=1) - 1
                if 0 <= motor_num < len(MOTOR_NAMES):
                    motor_name = MOTOR_NAMES[motor_num]
                    current = bus.sync_read("Present_Position", [motor_name], normalize=False)
                    console.print(f"[dim]Current: {current[motor_name]}[/dim]")

                    pos = IntPrompt.ask("Target (0-4095)")
                    if 0 <= pos <= 4095:
                        bus.sync_write("Torque_Enable", {motor_name: 1}, normalize=False)
                        bus.sync_write("Goal_Position", {motor_name: pos}, normalize=False)
                        console.print(f"[green]Moving {motor_name} → {pos}[/green]")
                    else:
                        console.print("[red]Invalid position[/red]")
                else:
                    console.print("[red]Invalid motor[/red]")
            except ValueError:
                console.print("[red]Invalid input[/red]")

    bus.sync_write("Torque_Enable", {name: 0 for name in MOTOR_NAMES}, normalize=False)
    bus.disconnect()
    console.print("[dim]Disconnected[/dim]")


if __name__ == "__main__":
    main()
