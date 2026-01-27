#!/usr/bin/env python3
"""Calibrate SO-101 arms."""
import os

from dotenv import load_dotenv
from rich.console import Console
from rich.prompt import Prompt

from lerobot.teleoperators.so_leader import SO101LeaderConfig, SO101Leader
from lerobot.robots.so_follower import SO101FollowerConfig, SO101Follower

load_dotenv()

console = Console()
LEADER_PORT = os.getenv("LEADER_ARM_PORT")
FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")


def calibrate_leader():
    console.print(f"[bold]Calibrating leader[/bold] [dim]({LEADER_PORT})[/dim]")
    leader = SO101Leader(SO101LeaderConfig(port=LEADER_PORT, id="leader_arm"))
    leader.connect(calibrate=False)
    leader.calibrate()
    leader.disconnect()
    console.print("[green]Leader calibrated[/green]\n")


def calibrate_follower():
    console.print(f"[bold]Calibrating follower[/bold] [dim]({FOLLOWER_PORT})[/dim]")
    follower = SO101Follower(SO101FollowerConfig(port=FOLLOWER_PORT, id="follower_arm"))
    follower.connect(calibrate=False)
    follower.calibrate()
    follower.disconnect()
    console.print("[green]Follower calibrated[/green]\n")


def select_arm():
    """Prompt user to select which arm to calibrate."""
    console.print("\n[bold]Select arm to calibrate:[/bold]")
    console.print(f"  [cyan]1[/cyan] Leader   [dim]({LEADER_PORT})[/dim]")
    console.print(f"  [cyan]2[/cyan] Follower [dim]({FOLLOWER_PORT})[/dim]")
    console.print(f"  [cyan]3[/cyan] Both")

    return Prompt.ask("Choice", choices=["1", "2", "3"])


if __name__ == "__main__":
    choice = select_arm()

    if choice == "1" and LEADER_PORT:
        calibrate_leader()
    elif choice == "2" and FOLLOWER_PORT:
        calibrate_follower()
    elif choice == "3":
        if LEADER_PORT:
            calibrate_leader()
        if FOLLOWER_PORT:
            calibrate_follower()

    console.print("[bold green]Done[/bold green]")
