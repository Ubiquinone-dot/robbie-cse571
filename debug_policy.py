#!/usr/bin/env python3
"""Debug script to check policy outputs."""
import torch
from lerobot.policies.act.modeling_act import ACTPolicy

CHECKPOINT = "checkpoints/multi_p2_8gpu_ep48/pretrained_model"

print(f"Loading policy from {CHECKPOINT}...")
policy = ACTPolicy.from_pretrained(CHECKPOINT)
policy.to("mps")
policy.eval()

print(f"Config device: {policy.config.device}")
print(f"Input features: {policy.config.input_features}")
print(f"Output features: {policy.config.output_features}")
print(f"n_action_steps: {policy.config.n_action_steps}")
print(f"chunk_size: {policy.config.chunk_size}")

# Create dummy observation matching expected input
dummy_state = torch.randn(1, 6, device="mps")  # [batch, 6 motors]
dummy_image = torch.randn(1, 3, 480, 640, device="mps")  # [batch, C, H, W]

obs = {
    "observation.state": dummy_state,
    "observation.images.front": dummy_image,
}

print("\nRunning inference with dummy data...")
with torch.no_grad():
    action = policy.select_action(obs)

print(f"Action shape: {action.shape}")
print(f"Action values: {action}")
print(f"Action min: {action.min().item():.4f}, max: {action.max().item():.4f}")
print(f"Action mean: {action.mean().item():.4f}, std: {action.std().item():.4f}")
