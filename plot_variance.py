#!/usr/bin/env python3
"""Plot variance analysis for robot demonstration dataset."""

from datasets import load_dataset
import numpy as np
import matplotlib.pyplot as plt

MOTOR_NAMES = ['shoulder_pan', 'shoulder_lift', 'elbow_flex', 'wrist_flex', 'wrist_roll', 'gripper']

def main():
    print("Loading dataset...")
    ds = load_dataset('Jbutch/record-prod', split='train')

    actions = np.array(ds['action'])
    episode_indices = np.array(ds['episode_index'])
    num_episodes = len(set(episode_indices))

    # Calculate variance metrics
    overall_variance = actions.var(axis=0)
    overall_std = actions.std(axis=0)

    # Per-episode variance
    episode_variances = []
    for ep in range(num_episodes):
        mask = episode_indices == ep
        ep_var = actions[mask].var(axis=0)
        episode_variances.append(ep_var)
    episode_variances = np.array(episode_variances)

    # Cross-episode variance (variance of episode means)
    episode_means = np.array([actions[episode_indices == ep].mean(axis=0) for ep in range(num_episodes)])
    cross_episode_variance = episode_means.var(axis=0)

    # Create figure with 4 subplots
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Variance Analysis of Robot Demonstrations', fontsize=16, fontweight='bold')

    # Plot 1: Overall variance bar chart
    ax1 = axes[0, 0]
    colors = plt.cm.viridis(np.linspace(0.2, 0.8, 6))
    bars = ax1.bar(MOTOR_NAMES, overall_variance, color=colors, edgecolor='black')
    ax1.set_ylabel('Variance (degrees²)')
    ax1.set_title('Overall Variance per Motor')
    ax1.set_xticklabels(MOTOR_NAMES, rotation=45, ha='right')
    for bar, val in zip(bars, overall_variance):
        ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 20,
                f'{val:.1f}', ha='center', va='bottom', fontsize=9)
    ax1.grid(True, alpha=0.3, axis='y')

    # Plot 2: Within-episode vs Cross-episode variance (stacked)
    ax2 = axes[0, 1]
    x = np.arange(len(MOTOR_NAMES))
    width = 0.35
    within_ep_var = episode_variances.mean(axis=0)  # Average within-episode variance

    bars1 = ax2.bar(x - width/2, within_ep_var, width, label='Within-episode (avg)', color='steelblue', edgecolor='black')
    bars2 = ax2.bar(x + width/2, cross_episode_variance, width, label='Cross-episode', color='coral', edgecolor='black')

    ax2.set_ylabel('Variance (degrees²)')
    ax2.set_title('Within-Episode vs Cross-Episode Variance')
    ax2.set_xticks(x)
    ax2.set_xticklabels(MOTOR_NAMES, rotation=45, ha='right')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')

    # Plot 3: Variance per episode (heatmap)
    ax3 = axes[1, 0]
    im = ax3.imshow(episode_variances.T, aspect='auto', cmap='YlOrRd')
    ax3.set_yticks(range(len(MOTOR_NAMES)))
    ax3.set_yticklabels(MOTOR_NAMES)
    ax3.set_xticks(range(num_episodes))
    ax3.set_xticklabels([f'Ep {i}' for i in range(num_episodes)])
    ax3.set_title('Variance per Episode (Heatmap)')
    ax3.set_xlabel('Episode')
    cbar = plt.colorbar(im, ax=ax3)
    cbar.set_label('Variance (degrees²)')

    # Plot 4: Rolling variance over time (all episodes concatenated)
    ax4 = axes[1, 1]
    window = 50  # Rolling window size
    for i, name in enumerate(MOTOR_NAMES):
        # Calculate rolling variance
        data = actions[:, i]
        rolling_var = np.array([data[max(0, j-window):j+1].var() for j in range(len(data))])
        ax4.plot(rolling_var, label=name, alpha=0.8, linewidth=1)

    # Add episode boundaries
    for ep in range(1, num_episodes):
        first_idx = np.where(episode_indices == ep)[0][0]
        ax4.axvline(first_idx, color='gray', linestyle='--', alpha=0.5, linewidth=0.5)

    ax4.set_xlabel('Sample Index')
    ax4.set_ylabel('Rolling Variance (window=50)')
    ax4.set_title('Rolling Variance Over Time')
    ax4.legend(loc='upper right', fontsize=8)
    ax4.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('outputs/variance_analysis.png', dpi=150, bbox_inches='tight')
    print("Saved: outputs/variance_analysis.png")

    # Print summary
    print("\n" + "="*50)
    print("VARIANCE SUMMARY")
    print("="*50)
    print(f"{'Motor':<15} {'Variance':>12} {'Std Dev':>12}")
    print("-" * 40)
    for i, name in enumerate(MOTOR_NAMES):
        print(f"{name:<15} {overall_variance[i]:>12.2f} {overall_std[i]:>12.2f}")

if __name__ == "__main__":
    main()
