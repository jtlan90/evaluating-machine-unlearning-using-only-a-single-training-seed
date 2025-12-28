#!/usr/bin/env python3
"""
Create boxplot figures following Lanyon et al. (2025) style
Comparing Algorithm 1 vs Algorithm 2 distributions
"""
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# Load data
data_file = "results/data/MQ2007_all_results.csv"
df = pd.read_csv(data_file)

print(f"Loaded {len(df)} results from {data_file}")

# Prepare data
scenarios = ['clean', 'data_poison', 'model_poison']
methods = ['retrain', 'FedRemove', 'fedEraser', 'fineTuning', 'pga']

scenario_labels = {
    'clean': 'Clean', 
    'data_poison': 'Data Poisoning', 
    'model_poison': 'Model Poisoning'
}

method_labels = {
    'retrain': 'Retrain',
    'FedRemove': 'FedRemove',
    'fedEraser': 'FedEraser',
    'fineTuning': 'FineTuning',
    'pga': 'PGA'
}

algorithm_labels = {
    1: 'Algorithm 1\n(single training seed)',
    2: 'Algorithm 2\n(multiple training seeds)'
}

# Set style
sns.set_style("whitegrid")
plt.rcParams['font.size'] = 11

# ========================================================================== #
# Figure 1: Boxplots for each scenario (similar to Lanyon et al. Fig 1)
# ========================================================================== #

for scenario in scenarios:
    scenario_data = df[df['scenario'] == scenario].copy()
    
    # Filter to only include methods we want
    scenario_data = scenario_data[scenario_data['method'].isin(methods)]
    
    # Compute retrain quantiles for reference lines (from Algorithm 2)
    retrain_algo2 = scenario_data[(scenario_data['method'] == 'retrain') & 
                                   (scenario_data['algorithm'] == 2)]['ndcg']
    retrain_median = retrain_algo2.median()
    retrain_q25 = retrain_algo2.quantile(0.25)
    retrain_q75 = retrain_algo2.quantile(0.75)
    
    fig, ax = plt.subplots(figsize=(12, 7))
    
    # Create boxplot
    sns.boxplot(
        data=scenario_data,
        x='method',
        y='ndcg',
        hue='algorithm',
        order=methods,
        palette={1: '#3498db', 2: '#e74c3c'},
        ax=ax,
        showfliers=False,  # Don't show outliers as points (they're included in box)
        linewidth=1.5
    )
    
    # Add reference lines for retrain performance
    ax.axhline(y=retrain_median, color='gray', linestyle='-', 
              linewidth=2, alpha=0.5, zorder=1)
    ax.axhline(y=retrain_q25, color='gray', linestyle=':', 
              linewidth=1.5, alpha=0.5, zorder=1)
    ax.axhline(y=retrain_q75, color='gray', linestyle=':', 
              linewidth=1.5, alpha=0.5, zorder=1)
    
    # Labels and title
    ax.set_xlabel('Unlearning Method', fontsize=14, fontweight='bold')
    ax.set_ylabel('Final NDCG@10', fontsize=14, fontweight='bold')
    ax.set_title(f'{scenario_labels[scenario]} - Performance Distribution Comparison',
                fontsize=16, fontweight='bold', pad=20)
    
    # Update x-axis labels
    ax.set_xticklabels([method_labels[m] for m in methods], 
                       fontsize=12, rotation=15, ha='right')
    
    # Update legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, [algorithm_labels[1], algorithm_labels[2]],
             title='Evaluation Protocol', fontsize=11, title_fontsize=12,
             loc='lower right', frameon=True, shadow=True)
    
    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', zorder=0)
    ax.set_axisbelow(True)
    
    plt.tight_layout()
    
    # Save
    output_path = f"results/figure_boxplot_{scenario}.pdf"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    output_path_png = f"results/figure_boxplot_{scenario}.png"
    plt.savefig(output_path_png, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"✅ Saved: {output_path}")
    print(f"✅ Saved: {output_path_png}")

# ========================================================================== #
# Figure 2: Combined multi-panel figure (all scenarios)
# ========================================================================== #

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Evaluation Protocol Sensitivity: Algorithm 1 vs Algorithm 2',
             fontsize=18, fontweight='bold', y=1.02)

for idx, scenario in enumerate(scenarios):
    ax = axes[idx]
    scenario_data = df[df['scenario'] == scenario].copy()
    scenario_data = scenario_data[scenario_data['method'].isin(methods)]
    
    # Compute retrain quantiles for reference lines
    retrain_algo2 = scenario_data[(scenario_data['method'] == 'retrain') & 
                                   (scenario_data['algorithm'] == 2)]['ndcg']
    retrain_median = retrain_algo2.median()
    retrain_q25 = retrain_algo2.quantile(0.25)
    retrain_q75 = retrain_algo2.quantile(0.75)
    
    # Create boxplot
    sns.boxplot(
        data=scenario_data,
        x='method',
        y='ndcg',
        hue='algorithm',
        order=methods,
        palette={1: '#3498db', 2: '#e74c3c'},
        ax=ax,
        showfliers=False,
        linewidth=1.2
    )
    
    # Add reference lines
    ax.axhline(y=retrain_median, color='gray', linestyle='-', 
              linewidth=1.5, alpha=0.5, zorder=1)
    ax.axhline(y=retrain_q25, color='gray', linestyle=':', 
              linewidth=1, alpha=0.5, zorder=1)
    ax.axhline(y=retrain_q75, color='gray', linestyle=':', 
              linewidth=1, alpha=0.5, zorder=1)
    
    # Labels
    ax.set_xlabel('Method', fontsize=12, fontweight='bold')
    if idx == 0:
        ax.set_ylabel('Final NDCG@10', fontsize=12, fontweight='bold')
    else:
        ax.set_ylabel('')
    
    ax.set_title(scenario_labels[scenario], fontsize=14, fontweight='bold', pad=10)
    
    # Update x-axis labels
    ax.set_xticklabels([method_labels[m] for m in methods], 
                       fontsize=10, rotation=30, ha='right')
    
    # Remove individual legends
    if ax.get_legend():
        ax.get_legend().remove()
    
    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', zorder=0)
    ax.set_axisbelow(True)

# Single legend for entire figure
handles, labels = axes[0].get_legend_handles_labels()
fig.legend(handles[:2], [algorithm_labels[1], algorithm_labels[2]],
          title='Evaluation Protocol',
          loc='upper center', bbox_to_anchor=(0.5, 0.98),
          fontsize=11, title_fontsize=12, ncol=2,
          frameon=True, shadow=True)

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save
output_path = "results/figure_boxplot_combined.pdf"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
output_path_png = "results/figure_boxplot_combined.png"
plt.savefig(output_path_png, dpi=300, bbox_inches='tight')
plt.close()

print(f"✅ Saved: {output_path}")
print(f"✅ Saved: {output_path_png}")

# ========================================================================== #
# Figure 3: FedRemove focused comparison (showing the problem)
# ========================================================================== #

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('FedRemove: Single-Seed vs Multi-Seed Evaluation',
             fontsize=18, fontweight='bold', y=1.02)

for idx, scenario in enumerate(scenarios):
    ax = axes[idx]
    
    # Get only FedRemove data
    fedremove_data = df[(df['scenario'] == scenario) & 
                        (df['method'] == 'FedRemove')].copy()
    
    # Get retrain for reference
    retrain_data = df[(df['scenario'] == scenario) & 
                      (df['method'] == 'retrain') & 
                      (df['algorithm'] == 2)].copy()
    
    # Create boxplot
    sns.boxplot(
        data=fedremove_data,
        x='algorithm',
        y='ndcg',
        order=[1, 2],
        palette={1: '#3498db', 2: '#e74c3c'},
        ax=ax,
        showfliers=True,  # Show outliers for FedRemove
        linewidth=2
    )
    
    # Add retrain median as reference
    retrain_median = retrain_data['ndcg'].median()
    ax.axhline(y=retrain_median, color='green', linestyle='--', 
              linewidth=2, alpha=0.7, label='Retrain (gold standard)', zorder=1)
    
    # Labels
    ax.set_xlabel('Evaluation Protocol', fontsize=12, fontweight='bold')
    if idx == 0:
        ax.set_ylabel('Final NDCG@10', fontsize=12, fontweight='bold')
    else:
        ax.set_ylabel('')
    
    ax.set_title(scenario_labels[scenario], fontsize=14, fontweight='bold', pad=10)
    
    # Update x-axis labels
    ax.set_xticklabels(['Algorithm 1\n(single seed)', 'Algorithm 2\n(multiple seeds)'], 
                       fontsize=11)
    
    # Grid
    ax.grid(axis='y', alpha=0.3, linestyle='--', zorder=0)
    ax.set_axisbelow(True)
    
    if idx == 2:
        ax.legend(fontsize=10, loc='lower right')

plt.tight_layout(rect=[0, 0, 1, 0.96])

# Save
output_path = "results/figure_fedremove_comparison.pdf"
plt.savefig(output_path, dpi=300, bbox_inches='tight')
output_path_png = "results/figure_fedremove_comparison.png"
plt.savefig(output_path_png, dpi=300, bbox_inches='tight')
plt.close()

print(f"✅ Saved: {output_path}")
print(f"✅ Saved: {output_path_png}")

print("\n" + "="*80)
print("📊 BOXPLOT FIGURES GENERATED")
print("="*80)
print("\nFollowing Lanyon et al. (2025) visualization style")
print("\nFiles created:")
print("  Individual scenarios:")
print("    - figure_boxplot_clean.pdf/png")
print("    - figure_boxplot_data_poison.pdf/png")
print("    - figure_boxplot_model_poison.pdf/png")
print("  Combined:")
print("    - figure_boxplot_combined.pdf/png")
print("  FedRemove focused:")
print("    - figure_fedremove_comparison.pdf/png")
print("\nThese show distributions (boxplots) not just summary statistics!")

