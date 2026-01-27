
# Follower calibration
```
lerobot-calibrate \
    --robot.type=so101_leader \
    --robot.port=/dev/tty.usbmodem5AE60552931 \
    --robot.id=leader_arm
```

# Leader
```
lerobot-calibrate \
    --teleop.type=so101_leader \
    --teleop.port=/dev/tty.usbmodem5AE60552931 \
    --teleop.id=leader_arm
```