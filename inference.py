#!/usr/bin/env python3
"""Run policy inference on SO101 follower arm."""

import os
import sys
from datetime import datetime

from dotenv import load_dotenv

from lerobot.cameras.opencv.configuration_opencv import OpenCVCameraConfig
from lerobot.datasets.lerobot_dataset import LeRobotDataset
from lerobot.datasets.pipeline_features import aggregate_pipeline_dataset_features, create_initial_features
from lerobot.datasets.utils import combine_feature_dicts
from lerobot.policies.act.modeling_act import ACTPolicy
from lerobot.policies.factory import make_pre_post_processors
from lerobot.processor import make_default_processors
from lerobot.robots.so_follower import SO101FollowerConfig, SO101Follower
from lerobot.scripts.lerobot_record import record_loop
from lerobot.utils.control_utils import init_keyboard_listener
from lerobot.utils.utils import log_say

# Load environment variables
load_dotenv()

# Configuration
NUM_EPISODES = 5
FPS = 30
EPISODE_TIME_SEC = 40
RESET_TIME_SEC = 10
TASK_DESCRIPTION = "pick up the black cube"

# Available policies on Hugging Face
HF_POLICIES = {
    "ep25": "Jbutch/policy_ep25",
    "ep10": "Jbutch/policy_ep10",
    "ep5": "Jbutch/policy_ep5",
}

# Get policy from command line or use default
POLICY_KEY = sys.argv[1] if len(sys.argv) > 1 else "ep25"
if POLICY_KEY not in HF_POLICIES:
    print(f"Error: Unknown policy '{POLICY_KEY}'")
    print("Available policies:")
    for key, repo in HF_POLICIES.items():
        print(f"  - {key} ({repo})")
    sys.exit(1)

POLICY_REPO = HF_POLICIES[POLICY_KEY]

# Get ports from environment
FOLLOWER_PORT = os.getenv("FOLLOWER_ARM_PORT")
HF_USER = os.getenv("HF_REPO_ID", "").split("/")[0]

if not FOLLOWER_PORT:
    print("Error: FOLLOWER_ARM_PORT not set in .env")
    sys.exit(1)

# Dataset ID with timestamp
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
HF_DATASET_ID = f"{HF_USER}/eval_{POLICY_KEY}_{timestamp}"

print(f"Running inference with:")
print(f"  Policy: {POLICY_KEY} ({POLICY_REPO})")
print(f"  Follower port: {FOLLOWER_PORT}")
print(f"  Task: {TASK_DESCRIPTION}")
print(f"  Dataset: {HF_DATASET_ID}")
print()

# Create the robot configuration
camera_config = {
    "front": OpenCVCameraConfig(
        index_or_path=0,
        width=640,
        height=480,
        fps=FPS,
    )
}
robot_config = SO101FollowerConfig(
    port=FOLLOWER_PORT,
    id="my_follower",
    cameras=camera_config,
)

# Initialize the robot
robot = SO101Follower(robot_config)

# Initialize the policy from Hugging Face
print(f"Loading policy from {POLICY_REPO}...")
policy = ACTPolicy.from_pretrained(POLICY_REPO)
policy.to("mps")  # Use MPS on macOS
policy.eval()
print("Policy loaded.")

# Create default robot processors (needed for feature aggregation)
teleop_action_processor, robot_action_processor, robot_observation_processor = make_default_processors()

# Configure the dataset features using the same method as lerobot_record
dataset_features = combine_feature_dicts(
    aggregate_pipeline_dataset_features(
        pipeline=teleop_action_processor,
        initial_features=create_initial_features(action=robot.action_features),
        use_videos=True,
    ),
    aggregate_pipeline_dataset_features(
        pipeline=robot_observation_processor,
        initial_features=create_initial_features(observation=robot.observation_features),
        use_videos=True,
    ),
)

# Create the dataset
dataset = LeRobotDataset.create(
    repo_id=HF_DATASET_ID,
    fps=FPS,
    features=dataset_features,
    robot_type=robot.name,
    use_videos=True,
    image_writer_threads=4,
)

# Initialize the keyboard listener
listener, events = init_keyboard_listener()

# Connect the robot
print("Connecting to robot...")
robot.connect()
print("Robot connected.")

# Create pre/post processors with device override for macOS
preprocessor, postprocessor = make_pre_post_processors(
    policy_cfg=policy.config,
    pretrained_path=POLICY_REPO,
    dataset_stats=dataset.meta.stats,
    preprocessor_overrides={
        "device_processor": {"device": "mps"},
    },
)

try:
    for episode_idx in range(NUM_EPISODES):
        if events["stop_recording"]:
            break

        log_say(f"Running inference, recording eval episode {episode_idx + 1} of {NUM_EPISODES}")
        print(f"Starting record_loop for episode {episode_idx + 1}...")

        # Run the policy inference loop
        record_loop(
            robot=robot,
            events=events,
            fps=FPS,
            teleop_action_processor=teleop_action_processor,
            robot_action_processor=robot_action_processor,
            robot_observation_processor=robot_observation_processor,
            policy=policy,
            preprocessor=preprocessor,
            postprocessor=postprocessor,
            dataset=dataset,
            control_time_s=EPISODE_TIME_SEC,
            single_task=TASK_DESCRIPTION,
            display_data=False,
        )

        if events["rerecord_episode"]:
            log_say("Re-recording episode")
            events["rerecord_episode"] = False
            events["exit_early"] = False
            dataset.clear_episode_buffer()
            continue

        dataset.save_episode()

        # Reset time between episodes (except last)
        if episode_idx < NUM_EPISODES - 1 and not events["stop_recording"]:
            log_say("Reset the environment")
            record_loop(
                robot=robot,
                events=events,
                fps=FPS,
                teleop_action_processor=teleop_action_processor,
                robot_action_processor=robot_action_processor,
                robot_observation_processor=robot_observation_processor,
                control_time_s=RESET_TIME_SEC,
                single_task=TASK_DESCRIPTION,
                display_data=False,
            )

finally:
    log_say("Stop recording", blocking=True)

    if robot.is_connected:
        robot.disconnect()

    if listener:
        listener.stop()

    dataset.finalize()

    # Optionally push to hub
    # dataset.push_to_hub()

    log_say("Done")
