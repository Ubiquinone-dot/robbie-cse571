#!/usr/bin/env python3
"""Live preview of camera 0 for focus/exposure tuning."""
import cv2
import sys

cam = cv2.VideoCapture(0, cv2.CAP_AVFOUNDATION)
if not cam.isOpened():
    cam = cv2.VideoCapture(0)

if not cam.isOpened():
    print("Failed to open camera 0!")
    sys.exit(1)

cam.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

print("Streaming camera 0. Press 'q' to quit, 's' to save snapshot.")

while True:
    ret, frame = cam.read()
    if not ret:
        continue
    cv2.imshow("Camera 0 Preview (q=quit, s=save)", frame)
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('s'):
        cv2.imwrite("outputs/camera_test/snapshot_0.png", frame)
        print("Saved snapshot.")

cam.release()
cv2.destroyAllWindows()
