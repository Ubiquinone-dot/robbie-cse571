#!/bin/bash
# Kill any zombie lerobot/inference processes that may be holding camera or serial ports

KILLED=0

for proc in lerobot-record lerobot-find-cameras "inference.py" "reset.py" "test_motors.py"; do
    pids=$(pgrep -f "$proc" 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "Killing $proc: $pids"
        kill $pids 2>/dev/null
        sleep 0.5
        # Force kill any that didn't die
        for pid in $pids; do
            if kill -0 "$pid" 2>/dev/null; then
                echo "  Force killing $pid"
                kill -9 "$pid" 2>/dev/null
            fi
        done
        KILLED=1
    fi
done

# Also kill orphaned multiprocessing resource trackers
pids=$(pgrep -f "multiprocessing.resource_tracker" 2>/dev/null)
if [ -n "$pids" ]; then
    echo "Killing resource trackers: $pids"
    kill -9 $pids 2>/dev/null
    KILLED=1
fi

if [ "$KILLED" = "0" ]; then
    echo "No zombie processes found."
else
    echo "Cleanup done."
fi
