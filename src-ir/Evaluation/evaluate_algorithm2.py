#!/usr/bin/env python3
"""
Evaluation script for Algorithm 2 results
Algorithm 2: Multiple training seeds (1-10), matching unlearning seeds (1-10)
Shows variance due to pre-training randomness
"""
import os
import sys
import pickle
import numpy as np
import argparse
import matplotlib.pyplot as plt
import seaborn as sns

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

def parse_args():
    parser = argparse.ArgumentParser(description='Evaluate Algorithm 2 results')
    parser.add_argument('--base_dir', type=str, default='../save',
                        help='Base directory containing results')
    parser.add_argument('--dataset', type=str, default='MQ2007',
                        choices=['MQ2007', 'MSLR10K', 'istella-s', 'Yahoo'],
                        help='Dataset to evaluate')
    parser.add_argument('--seed_start', type=int, default=1,
                        help='Start of seed range')
    parser.add_argument('--seed_end', type=int, default=10,
                        help='End of seed range')
    parser.add_argument('--save_dir', type=str, default='results/algorithm2',
                        help='Directory to save results')
    return parser.parse_args()

def load_training_results(base_dir, dataset, scenario, model, fold, seed_start, seed_end):
    """Load training results across multiple seeds"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    results = []
    for seed in range(seed_start, seed_end + 1):
        path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{seed}_state_1000.pkl"
        try:
            with open(path, 'rb') as f:
                result = pickle.load(f)
                if hasattr(result, 'ndcg_server'):
                    results.append(result.ndcg_server[:1000])
        except FileNotFoundError:
            print(f"Warning: Training file not found - {path}")
    
    return np.array(results) if results else None

def load_unlearning_results(base_dir, dataset, scenario, model, fold, seed_start, seed_end, method):
    """Load unlearning results where train_seed == unlearn_seed"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    results = []
    for seed in range(seed_start, seed_end + 1):
        path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{seed}_unlearning_{method}_seed{seed}_1000.pkl"
        try:
            with open(path, 'rb') as f:
                result = pickle.load(f)
                if hasattr(result, 'ndcg_server'):
                    results.append(result.ndcg_server[:1000])
        except FileNotFoundError:
            print(f"Warning: Unlearning file not found - {path}")
    
    return np.array(results) if results else None

def plot_scenario_results(base_dir, dataset, scenario, seed_start, seed_end, save_dir):
    """Plot results for one scenario showing mean and variance across seeds"""
    models = ['Perfect', 'Navigational', 'Informational']
    methods = ['retrain', 'FedRemove', 'fedEraser', 'fineTuning', 'pga']
    
    sns.set_style("whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(36, 8))
    
    colors = {
        'training': 'blue',
        'retrain': 'green',
        'FedRemove': 'orange',
        'fedEraser': 'red',
        'fineTuning': 'cyan',
        'pga': 'magenta'
    }
    
    for j, model in enumerate(models):
        ax = axes[j]
        
        # Plot training phase (multiple runs with mean and std)
        training_results = load_training_results(base_dir, dataset, scenario, model, 1, 
                                                 seed_start, seed_end)
        if training_results is not None and len(training_results) > 0:
            epochs = np.arange(0, 1000)
            mean_ndcg = np.mean(training_results, axis=0)
            std_ndcg = np.std(training_results, axis=0)
            
            # Plot individual training runs with transparency to show outliers
            for i, seed_result in enumerate(training_results):
                ax.plot(epochs, seed_result, color=colors['training'], 
                       linewidth=0.5, alpha=0.3, zorder=1)
            
            # Plot mean with thicker line
            ax.plot(epochs, mean_ndcg, color=colors['training'], linewidth=2.5,
                   label=f'Training (n={len(training_results)})', alpha=0.8, zorder=2)
            ax.fill_between(epochs, mean_ndcg - std_ndcg, mean_ndcg + std_ndcg,
                           color=colors['training'], alpha=0.15, zorder=0)
        
        # Plot unlearning phase (multiple runs with mean and std)
        for method in methods:
            unlearn_results = load_unlearning_results(
                base_dir, dataset, scenario, model, 1, seed_start, seed_end, method
            )
            
            if unlearn_results is not None and len(unlearn_results) > 0:
                epochs = np.arange(1000, 2000)
                mean_ndcg = np.mean(unlearn_results, axis=0)
                std_ndcg = np.std(unlearn_results, axis=0)
                
                # Plot individual runs with transparency to show outliers
                for i, seed_result in enumerate(unlearn_results):
                    ax.plot(epochs, seed_result, color=colors[method], 
                           linewidth=0.5, alpha=0.3, zorder=1)
                
                # Plot mean with thicker line
                ax.plot(epochs, mean_ndcg, color=colors[method], linewidth=2.5,
                       label=f'{method} (n={len(unlearn_results)})', zorder=2)
                # Keep std shading but lighter
                ax.fill_between(epochs, mean_ndcg - std_ndcg, mean_ndcg + std_ndcg,
                               color=colors[method], alpha=0.15, zorder=0)
        
        ax.set_title(f'{model}', fontsize=28, fontweight='bold')
        ax.set_xlabel('Epoch', fontsize=24, fontweight='bold')
        ax.set_ylabel('Offline NDCG@10', fontsize=24, fontweight='bold')
        ax.tick_params(axis='both', which='major', labelsize=20)
        ax.axvline(x=1000, color='gray', linestyle='--', alpha=0.5, linewidth=2)
        ax.grid(True, alpha=0.3)
        
        # Add phase labels
        ax.text(500, ax.get_ylim()[0] * 1.02, 'Training',
               horizontalalignment='center', fontsize=22, fontweight='bold')
        ax.text(1500, ax.get_ylim()[0] * 1.02, 'Unlearning',
               horizontalalignment='center', fontsize=22, fontweight='bold')
    
    # Single legend for all subplots
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.08),
              fontsize=24, ncol=6, frameon=True, shadow=True)
    
    plt.tight_layout()
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{dataset}_{scenario}_algorithm2.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved plot to {save_path}")

if __name__ == "__main__":
    args = parse_args()
    
    print(f"Evaluating Algorithm 2 results for {args.dataset}")
    print(f"Seed range: {args.seed_start}-{args.seed_end}")
    print("=" * 80)
    
    scenarios = ['clean', 'data_poison', 'model_poison']
    
    for scenario in scenarios:
        print(f"\nProcessing {scenario} scenario...")
        plot_scenario_results(args.base_dir, args.dataset, scenario,
                            args.seed_start, args.seed_end, args.save_dir)
    
    print("\n" + "=" * 80)
    print("Evaluation complete!")
    print(f"Generated 3 figures in {args.save_dir}/")
