#!/usr/bin/env python3
"""Calibrate SO-101 arms."""
import os

from dotenv import load_dotenv
from rich.console import Console

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


if __name__ == "__main__":
    if LEADER_PORT:
        calibrate_leader()
    if FOLLOWER_PORT:
        calibrate_follower()
    console.print("[bold green]Done[/bold green]")
