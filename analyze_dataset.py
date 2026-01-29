#!/usr/bin/env python3
"""Analyze robot demonstration dataset for consistency."""

from datasets import load_dataset
import numpy as np
import matplotlib.pyplot as plt

# Motor names for the SO-101 arm
MOTOR_NAMES = ['shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper']

def main():
    print("Loading dataset...")
    ds = load_dataset('Jbutch/record-prod', split='train')

    # Convert to numpy arrays
    actions = np.array(ds['action'])
    states = np.array(ds['observation.state'])
    episode_indices = np.array(ds['episode_index'])

    num_episodes = len(set(episode_indices))
    num_samples = len(ds)

    print(f"\n{'='*60}")
    print("DATASET OVERVIEW")
    print(f"{'='*60}")
    print(f"Total samples: {num_samples}")
    print(f"Number of episodes: {num_episodes}")
    print(f"Average samples per episode: {num_samples / num_episodes:.1f}")
    print(f"Action dimensions: {actions.shape[1]}")
    print(f"State dimensions: {states.shape[1]}")

    # Statistics per dimension
    print(f"\n{'='*60}")
    print("ACTION STATISTICS (per motor)")
    print(f"{'='*60}")
    print(f"{'Motor':<15} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10} {'Range':>10}")
    print("-" * 65)
    for i, name in enumerate(MOTOR_NAMES):
        col = actions[:, i]
        print(f"{name:<15} {col.mean():>10.2f} {col.std():>10.2f} {col.min():>10.2f} {col.max():>10.2f} {col.max()-col.min():>10.2f}")

    print(f"\n{'='*60}")
    print("STATE STATISTICS (per motor)")
    print(f"{'='*60}")
    print(f"{'Motor':<15} {'Mean':>10} {'Std':>10} {'Min':>10} {'Max':>10} {'Range':>10}")
    print("-" * 65)
    for i, name in enumerate(MOTOR_NAMES):
        col = states[:, i]
        print(f"{name:<15} {col.mean():>10.2f} {col.std():>10.2f} {col.min():>10.2f} {col.max():>10.2f} {col.max()-col.min():>10.2f}")

    # Per-episode consistency analysis
    print(f"\n{'='*60}")
    print("EPISODE CONSISTENCY ANALYSIS")
    print(f"{'='*60}")

    episode_lengths = []
    episode_action_means = []
    episode_action_stds = []

    for ep in range(num_episodes):
        mask = episode_indices == ep
        ep_actions = actions[mask]
        episode_lengths.append(len(ep_actions))
        episode_action_means.append(ep_actions.mean(axis=0))
        episode_action_stds.append(ep_actions.std(axis=0))

    episode_lengths = np.array(episode_lengths)
    episode_action_means = np.array(episode_action_means)
    episode_action_stds = np.array(episode_action_stds)

    print(f"\nEpisode lengths: {episode_lengths}")
    print(f"Length mean: {episode_lengths.mean():.1f}, std: {episode_lengths.std():.1f}")
    print(f"Length range: {episode_lengths.min()} - {episode_lengths.max()}")

    # Cross-episode consistency (std of means across episodes)
    print(f"\nCross-episode consistency (std of episode means):")
    print(f"{'Motor':<15} {'Action Std':>12} {'Interpretation':<20}")
    print("-" * 50)
    for i, name in enumerate(MOTOR_NAMES):
        std_of_means = episode_action_means[:, i].std()
        interpretation = "Very consistent" if std_of_means < 5 else "Consistent" if std_of_means < 15 else "Variable" if std_of_means < 30 else "Highly variable"
        print(f"{name:<15} {std_of_means:>12.2f} {interpretation:<20}")

    # Create histogram plots
    print(f"\n{'='*60}")
    print("GENERATING HISTOGRAMS...")
    print(f"{'='*60}")

    # Figure 1: Action histograms
    fig1, axes1 = plt.subplots(2, 3, figsize=(14, 8))
    fig1.suptitle('Action Distribution by Motor (All Episodes)', fontsize=14, fontweight='bold')

    for i, (ax, name) in enumerate(zip(axes1.flat, MOTOR_NAMES)):
        data = actions[:, i]
        ax.hist(data, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
        ax.axvline(data.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {data.mean():.1f}')
        ax.axvline(data.mean() - data.std(), color='orange', linestyle=':', linewidth=1.5)
        ax.axvline(data.mean() + data.std(), color='orange', linestyle=':', linewidth=1.5, label=f'±1 Std: {data.std():.1f}')
        ax.set_xlabel('Position (degrees)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{name}')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig1.savefig('outputs/action_histograms.png', dpi=150, bbox_inches='tight')
    print("Saved: outputs/action_histograms.png")

    # Figure 2: State histograms
    fig2, axes2 = plt.subplots(2, 3, figsize=(14, 8))
    fig2.suptitle('State Distribution by Motor (All Episodes)', fontsize=14, fontweight='bold')

    for i, (ax, name) in enumerate(zip(axes2.flat, MOTOR_NAMES)):
        data = states[:, i]
        ax.hist(data, bins=50, edgecolor='black', alpha=0.7, color='forestgreen')
        ax.axvline(data.mean(), color='red', linestyle='--', linewidth=2, label=f'Mean: {data.mean():.1f}')
        ax.axvline(data.mean() - data.std(), color='orange', linestyle=':', linewidth=1.5)
        ax.axvline(data.mean() + data.std(), color='orange', linestyle=':', linewidth=1.5, label=f'±1 Std: {data.std():.1f}')
        ax.set_xlabel('Position (degrees)')
        ax.set_ylabel('Frequency')
        ax.set_title(f'{name}')
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig2.savefig('outputs/state_histograms.png', dpi=150, bbox_inches='tight')
    print("Saved: outputs/state_histograms.png")

    # Figure 3: Per-episode comparison (boxplots)
    fig3, axes3 = plt.subplots(2, 3, figsize=(14, 8))
    fig3.suptitle('Action Distribution per Episode (Boxplots)', fontsize=14, fontweight='bold')

    for i, (ax, name) in enumerate(zip(axes3.flat, MOTOR_NAMES)):
        episode_data = [actions[episode_indices == ep, i] for ep in range(num_episodes)]
        bp = ax.boxplot(episode_data, patch_artist=True)
        for patch in bp['boxes']:
            patch.set_facecolor('lightblue')
        ax.set_xlabel('Episode')
        ax.set_ylabel('Position (degrees)')
        ax.set_title(f'{name}')
        ax.grid(True, alpha=0.3, axis='y')

    plt.tight_layout()
    fig3.savefig('outputs/episode_boxplots.png', dpi=150, bbox_inches='tight')
    print("Saved: outputs/episode_boxplots.png")

    # Figure 4: Time series overlay for each motor
    fig4, axes4 = plt.subplots(2, 3, figsize=(14, 8))
    fig4.suptitle('Action Trajectories Overlaid (All Episodes)', fontsize=14, fontweight='bold')

    colors = plt.cm.tab10(np.linspace(0, 1, num_episodes))

    for i, (ax, name) in enumerate(zip(axes4.flat, MOTOR_NAMES)):
        for ep in range(num_episodes):
            mask = episode_indices == ep
            ep_actions = actions[mask, i]
            # Normalize time to [0, 1] for overlay
            t = np.linspace(0, 1, len(ep_actions))
            ax.plot(t, ep_actions, color=colors[ep], alpha=0.6, linewidth=1, label=f'Ep {ep}')
        ax.set_xlabel('Normalized Time')
        ax.set_ylabel('Position (degrees)')
        ax.set_title(f'{name}')
        ax.grid(True, alpha=0.3)

    # Add single legend
    handles, labels = axes4.flat[0].get_legend_handles_labels()
    fig4.legend(handles, labels, loc='upper right', ncol=5, fontsize=8)

    plt.tight_layout(rect=[0, 0, 1, 0.95])
    fig4.savefig('outputs/trajectory_overlay.png', dpi=150, bbox_inches='tight')
    print("Saved: outputs/trajectory_overlay.png")

    print(f"\n{'='*60}")
    print("CONSISTENCY SUMMARY")
    print(f"{'='*60}")

    # Overall consistency score based on coefficient of variation
    cv_actions = actions.std(axis=0) / (np.abs(actions.mean(axis=0)) + 1e-6)
    cv_states = states.std(axis=0) / (np.abs(states.mean(axis=0)) + 1e-6)

    print("\nCoefficient of Variation (lower = more consistent):")
    print(f"{'Motor':<15} {'Action CV':>12} {'State CV':>12}")
    print("-" * 40)
    for i, name in enumerate(MOTOR_NAMES):
        print(f"{name:<15} {cv_actions[i]:>12.3f} {cv_states[i]:>12.3f}")

    overall_action_cv = cv_actions.mean()
    overall_state_cv = cv_states.mean()

    print(f"\nOverall Action CV: {overall_action_cv:.3f}")
    print(f"Overall State CV: {overall_state_cv:.3f}")

    if overall_action_cv < 0.5:
        print("\nAssessment: HIGHLY CONSISTENT demonstrations")
    elif overall_action_cv < 1.0:
        print("\nAssessment: MODERATELY CONSISTENT demonstrations")
    else:
        print("\nAssessment: VARIABLE demonstrations - consider recording more uniform examples")

    print(f"\nAll plots saved to outputs/ directory")

if __name__ == "__main__":
    main()
