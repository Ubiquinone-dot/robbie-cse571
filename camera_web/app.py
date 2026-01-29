import json
import os
import socket
import threading
import time

import cv2
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, render_template_string
from lerobot.cameras.configs import ColorMode, Cv2Rotation
from lerobot.cameras.opencv.camera_opencv import OpenCVCamera
from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.motors.feetech import FeetechMotorsBus
from lerobot.motors.motors_bus import Motor, MotorNormMode

load_dotenv()

app = Flask(__name__)

# Camera configuration
CAMERA_CONFIG = OpenCVCameraConfig(
    index_or_path=0,
    fps=15,
    width=1920,
    height=1080,
    color_mode=ColorMode.RGB,
    rotation=Cv2Rotation.NO_ROTATION,
)

# Motor configuration
LEADER_PORT = os.getenv("LEADER_ARM_PORT")
FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")
MOTOR_NAMES = ["shoulder_pan", "shoulder_lift", "elbow_flex", "wrist_flex", "wrist_roll", "gripper"]
MOTOR_IDS = {name: i + 1 for i, name in enumerate(MOTOR_NAMES)}

# Global state
camera = None
camera_lock = threading.Lock()

robot_state = {
    "leader": {"connected": False, "bus": None, "data": {}},
    "follower": {"connected": False, "bus": None, "data": {}},
}
robot_lock = threading.Lock()


def create_bus(port):
    return FeetechMotorsBus(
        port=port,
        motors={
            name: Motor(id=id_, model="sts3215", norm_mode=MotorNormMode.RANGE_M100_100)
            for name, id_ in MOTOR_IDS.items()
        },
    )


def connect_camera():
    """Connect to camera using lerobot API."""
    global camera
    with camera_lock:
        if camera is not None:
            try:
                camera.disconnect()
            except Exception:
                pass
        try:
            camera = OpenCVCamera(CAMERA_CONFIG)
            camera.connect()
            print("Camera connected")
        except Exception as e:
            print(f"Failed to connect camera: {e}")
            camera = None


def connect_robots():
    """Connect to robot arms."""
    with robot_lock:
        for arm, port in [("leader", LEADER_PORT), ("follower", FOLLOWER_PORT)]:
            if port:
                try:
                    bus = create_bus(port)
                    bus.connect()
                    robot_state[arm]["bus"] = bus
                    robot_state[arm]["connected"] = True
                    print(f"Connected to {arm} arm on {port}")
                except Exception as e:
                    print(f"Failed to connect to {arm} arm: {e}")
                    robot_state[arm]["connected"] = False


def read_robot_data():
    """Read data from connected robots."""
    with robot_lock:
        for arm in ["leader", "follower"]:
            if robot_state[arm]["connected"] and robot_state[arm]["bus"]:
                try:
                    bus = robot_state[arm]["bus"]
                    voltage = bus.sync_read("Present_Voltage", normalize=False)
                    temp = bus.sync_read("Present_Temperature", normalize=False)
                    load = bus.sync_read("Present_Load", normalize=False)
                    current = bus.sync_read("Present_Current", normalize=False)
                    position = bus.sync_read("Present_Position", normalize=False)

                    motors = {}
                    for name in MOTOR_NAMES:
                        motors[name] = {
                            "voltage": voltage[name] / 10,
                            "temp": temp[name],
                            "load": load[name],
                            "current": current[name],
                            "position": position[name],  # Raw 0-4095 value
                        }

                    robot_state[arm]["data"] = {
                        "motors": motors,
                        "min_voltage": min(m["voltage"] for m in motors.values()),
                        "max_temp": max(m["temp"] for m in motors.values()),
                        "timestamp": time.time(),
                    }
                except Exception as e:
                    print(f"Error reading {arm} arm: {e}")
                    robot_state[arm]["connected"] = False


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>LeRobot Dashboard</title>
    <style>
        * { box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 0;
            padding: 20px;
            background: #0f0f0f;
            color: #e0e0e0;
        }
        h1 {
            text-align: center;
            color: #fff;
            margin-bottom: 20px;
        }
        .dashboard {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }
        .panel {
            background: #1a1a1a;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        }
        .panel h2 {
            margin: 0 0 15px 0;
            font-size: 1.2em;
            color: #fff;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .status-dot {
            width: 10px;
            height: 10px;
            border-radius: 50%;
            display: inline-block;
        }
        .status-dot.connected { background: #4caf50; }
        .status-dot.disconnected { background: #f44336; }
        .camera-container img {
            width: 100%;
            border-radius: 8px;
        }
        .sidebar {
            display: flex;
            flex-direction: column;
            gap: 20px;
        }
        .motor-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 8px;
        }
        .motor-card {
            background: #252525;
            border-radius: 8px;
            padding: 10px;
        }
        .motor-card h3 {
            margin: 0 0 6px 0;
            font-size: 0.75em;
            color: #888;
            text-transform: uppercase;
        }
        .motor-stats {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 4px;
            font-size: 0.8em;
        }
        .stat {
            display: flex;
            justify-content: space-between;
        }
        .stat-label { color: #666; }
        .stat-value { font-weight: 600; }
        .stat-value.warning { color: #ff9800; }
        .stat-value.danger { color: #f44336; }
        .stat-value.good { color: #4caf50; }
        .summary {
            display: flex;
            gap: 15px;
            margin-top: 12px;
            padding-top: 12px;
            border-top: 1px solid #333;
        }
        .summary-item {
            display: flex;
            flex-direction: column;
        }
        .summary-label { font-size: 0.7em; color: #666; }
        .summary-value { font-size: 1.1em; font-weight: 600; }
        .position-bar {
            height: 3px;
            background: #333;
            border-radius: 2px;
            margin-top: 6px;
            overflow: hidden;
        }
        .position-fill {
            height: 100%;
            background: #2196f3;
            border-radius: 2px;
            transition: width 0.1s;
        }
        .disconnected-msg {
            color: #666;
            text-align: center;
            padding: 30px 10px;
        }
        .controls {
            display: flex;
            gap: 10px;
            justify-content: center;
        }
        button {
            background: #2196f3;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 6px;
            cursor: pointer;
            font-size: 0.9em;
        }
        button:hover { background: #1976d2; }
    </style>
</head>
<body>
    <h1>LeRobot Dashboard</h1>

    <div class="dashboard">
        <div class="panel camera-container">
            <h2>Camera Feed</h2>
            <img src="/video_feed" alt="Camera Stream">
        </div>

        <div class="sidebar">
            <div class="panel" id="leader-panel">
                <h2>
                    <span class="status-dot disconnected" id="leader-status"></span>
                    Leader Arm
                </h2>
                <div id="leader-content">
                    <div class="disconnected-msg">Connecting...</div>
                </div>
            </div>

            <div class="panel" id="follower-panel">
                <h2>
                    <span class="status-dot disconnected" id="follower-status"></span>
                    Follower Arm
                </h2>
                <div id="follower-content">
                    <div class="disconnected-msg">Connecting...</div>
                </div>
            </div>

            <div class="controls">
                <button onclick="reconnect()">Reconnect Arms</button>
            </div>
        </div>
    </div>

    <script>
        function getVoltageClass(v) {
            if (v < 6.0) return 'danger';
            if (v < 6.5) return 'warning';
            return 'good';
        }

        function getTempClass(t) {
            if (t > 60) return 'danger';
            if (t > 45) return 'warning';
            return 'good';
        }

        function renderArm(arm, data) {
            const statusDot = document.getElementById(`${arm}-status`);
            const content = document.getElementById(`${arm}-content`);

            if (!data.connected) {
                statusDot.className = 'status-dot disconnected';
                content.innerHTML = '<div class="disconnected-msg">Not connected</div>';
                return;
            }

            statusDot.className = 'status-dot connected';

            const motors = data.data.motors;
            let html = '<div class="motor-grid">';

            for (const [name, m] of Object.entries(motors)) {
                const displayName = name.replace('_', ' ');
                const posPercent = (m.position / 4095) * 100;  // Raw 0-4095 range

                html += `
                    <div class="motor-card">
                        <h3>${displayName}</h3>
                        <div class="motor-stats">
                            <div class="stat">
                                <span class="stat-label">Volt</span>
                                <span class="stat-value ${getVoltageClass(m.voltage)}">${m.voltage.toFixed(1)}V</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Temp</span>
                                <span class="stat-value ${getTempClass(m.temp)}">${m.temp}°C</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Load</span>
                                <span class="stat-value">${m.load}</span>
                            </div>
                            <div class="stat">
                                <span class="stat-label">Pos</span>
                                <span class="stat-value">${m.position}</span>
                            </div>
                        </div>
                        <div class="position-bar">
                            <div class="position-fill" style="width: ${posPercent}%"></div>
                        </div>
                    </div>
                `;
            }

            html += '</div>';
            html += `
                <div class="summary">
                    <div class="summary-item">
                        <span class="summary-label">Min Voltage</span>
                        <span class="summary-value ${getVoltageClass(data.data.min_voltage)}">${data.data.min_voltage.toFixed(1)}V</span>
                    </div>
                    <div class="summary-item">
                        <span class="summary-label">Max Temp</span>
                        <span class="summary-value ${getTempClass(data.data.max_temp)}">${data.data.max_temp}°C</span>
                    </div>
                </div>
            `;

            content.innerHTML = html;
        }

        async function fetchRobotData() {
            try {
                const response = await fetch('/robot_data');
                const data = await response.json();
                renderArm('leader', data.leader);
                renderArm('follower', data.follower);
            } catch (e) {
                console.error('Error fetching robot data:', e);
            }
        }

        async function reconnect() {
            try {
                await fetch('/reconnect', { method: 'POST' });
            } catch (e) {
                console.error('Error reconnecting:', e);
            }
        }

        // Poll for robot data every 200ms
        setInterval(fetchRobotData, 200);
        fetchRobotData();
    </script>
</body>
</html>
"""


def generate_frames():
    """Generate frames using lerobot camera API."""
    global camera

    while True:
        with camera_lock:
            if camera is None:
                time.sleep(0.1)
                continue
            try:
                # async_read returns RGB numpy array
                frame = camera.async_read(timeout_ms=200)
                # Convert RGB to BGR for cv2.imencode
                frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            except Exception as e:
                print(f"Camera read error: {e}")
                time.sleep(0.1)
                continue

        ret, buffer = cv2.imencode('.jpg', frame_bgr, [cv2.IMWRITE_JPEG_QUALITY, 80])
        if not ret:
            continue

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')


def robot_polling_thread():
    """Background thread to poll robot data."""
    while True:
        read_robot_data()
        time.sleep(0.1)


@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)


@app.route('/video_feed')
def video_feed():
    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/robot_data')
def robot_data():
    with robot_lock:
        return jsonify({
            "leader": {
                "connected": robot_state["leader"]["connected"],
                "data": robot_state["leader"]["data"],
            },
            "follower": {
                "connected": robot_state["follower"]["connected"],
                "data": robot_state["follower"]["data"],
            },
        })


@app.route('/reconnect', methods=['POST'])
def reconnect():
    # Disconnect existing
    with robot_lock:
        for arm in ["leader", "follower"]:
            if robot_state[arm]["bus"]:
                try:
                    robot_state[arm]["bus"].disconnect()
                except Exception:
                    pass
                robot_state[arm]["bus"] = None
                robot_state[arm]["connected"] = False

    # Reconnect
    connect_robots()
    return jsonify({"status": "ok"})


def find_available_port(start_port=5001, max_attempts=100):
    """Find an available port starting from start_port."""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts}")


if __name__ == '__main__':
    print("Connecting to camera...")
    connect_camera()

    print("Connecting to robot arms...")
    connect_robots()

    # Start background polling thread
    polling_thread = threading.Thread(target=robot_polling_thread, daemon=True)
    polling_thread.start()

    # Find available port
    port = find_available_port(5001)
    print(f"\n{'='*50}")
    print(f"Dashboard running at: http://localhost:{port}")
    print(f"{'='*50}\n")
    app.run(host='0.0.0.0', port=port, threaded=True)
