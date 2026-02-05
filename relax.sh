#!/bin/bash
# Relax all motors on SO-101 arms (disable torque and lock)
# Usage: ./relax.sh [leader|follower]  (defaults to both)

uv run python relax.py "$@"
