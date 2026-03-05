#!/usr/bin/env python3
"""Capture a snapshot from each available camera and save to outputs/camera_test/."""
import cv2
import os

os.makedirs("outputs/camera_test", exist_ok=True)

for idx in range(4):
    cap = cv2.VideoCapture(idx)
    if cap.isOpened():
        # Warm up with a few reads
        for _ in range(5):
            cap.read()
        ret, frame = cap.read()
        if ret:
            h, w = frame.shape[:2]
            path = f"outputs/camera_test/camera_{idx}.png"
            cv2.imwrite(path, frame)
            print(f"Camera {idx}: {w}x{h} -> {path}")
        else:
            print(f"Camera {idx}: opened but read failed")
        cap.release()
    else:
        print(f"Camera {idx}: not available")
