#!/usr/bin/env python3
"""Teleoperate the follower arm using the leader arm."""
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.live import Live
from rich.table import Table

from lerobot.teleoperators.so_leader import SO101LeaderConfig, SO101Leader
from lerobot.robots.so_follower import SO101FollowerConfig, SO101Follower

load_dotenv()

console = Console()
LEADER_PORT = os.getenv("LEADER_ARM_PORT")
FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")


def main():
    console.print(f"[dim]Leader:[/dim]   {LEADER_PORT}")
    console.print(f"[dim]Follower:[/dim] {FOLLOWER_PORT}")

    robot = SO101Follower(SO101FollowerConfig(port=FOLLOWER_PORT, id="follower_arm"))
    teleop = SO101Leader(SO101LeaderConfig(port=LEADER_PORT, id="leader_arm"))

    with console.status("[bold]Connecting..."):
        robot.connect()
        teleop.connect()

    console.print("[green]Connected[/green] — Move leader to control follower")
    console.print("[dim]Ctrl+C to stop[/dim]\n")

    try:
        while True:
            robot.send_action(teleop.get_action())
    except KeyboardInterrupt:
        console.print("\n[yellow]Stopping...[/yellow]")
    finally:
        teleop.disconnect()
        robot.disconnect()
        console.print("[dim]Disconnected[/dim]")


if __name__ == "__main__":
    main()
