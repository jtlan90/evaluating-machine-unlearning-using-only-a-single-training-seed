#!/usr/bin/env python3
"""
Evaluation script for Algorithm 1 results
Algorithm 1: Fixed training seed (1), multiple unlearning seeds (100-109)
Shows variance due to unlearning randomness
"""
import os
import sys
import pickle
import numpy as np
import argparse
import matplotlib.pyplot as plt
import seaborn as sns

def wasserstein_2_distance(u, v):
    """
    Compute Wasserstein-2 distance between two 1D distributions.
    W2 = sqrt(mean of squared differences of sorted quantiles)
    """
    u = np.asarray(u).flatten()
    v = np.asarray(v).flatten()
    
    u_sorted = np.sort(u)
    v_sorted = np.sort(v)
    
    # For equal-sized samples
    if len(u) == len(v):
        return np.sqrt(np.mean((u_sorted - v_sorted)**2))
    else:
        # For unequal sizes, need to interpolate to common quantiles
        n_u, n_v = len(u), len(v)
        all_quantiles = np.unique(np.concatenate([
            np.linspace(0, 1, n_u + 1),
            np.linspace(0, 1, n_v + 1)
        ]))
        
        u_quantiles = np.interp(all_quantiles, np.linspace(0, 1, n_u), u_sorted)
        v_quantiles = np.interp(all_quantiles, np.linspace(0, 1, n_v), v_sorted)
        
        return np.sqrt(np.trapz((u_quantiles - v_quantiles)**2, all_quantiles))
from glob import glob

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

def parse_args():
    parser = argparse.ArgumentParser(description='Evaluate Algorithm 1 results')
    parser.add_argument('--base_dir', type=str, default='../save',
                        help='Base directory containing results')
    parser.add_argument('--dataset', type=str, default='MQ2007',
                        choices=['MQ2007', 'MSLR10K', 'istella-s', 'Yahoo'],
                        help='Dataset to evaluate')
    parser.add_argument('--train_seed', type=int, default=1,
                        help='Training seed used in Algorithm 1')
    parser.add_argument('--unlearn_seed_start', type=int, default=100,
                        help='Start of unlearning seed range')
    parser.add_argument('--unlearn_seed_end', type=int, default=109,
                        help='End of unlearning seed range')
    parser.add_argument('--save_dir', type=str, default='results/algorithm1',
                        help='Directory to save results')
    return parser.parse_args()

def load_training_result(base_dir, dataset, scenario, model, fold, train_seed):
    """Load the single training result"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{train_seed}_state_1000.pkl"
    try:
        with open(path, 'rb') as f:
            result = pickle.load(f)
            return result.ndcg_server[:1000] if hasattr(result, 'ndcg_server') else None
    except FileNotFoundError:
        print(f"Warning: Training file not found - {path}")
        return None

def load_unlearning_results(base_dir, dataset, scenario, model, fold, train_seed, 
                            unlearn_seed_start, unlearn_seed_end, method):
    """Load all unlearning results for a given method across multiple unlearning seeds"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    results = []
    for unlearn_seed in range(unlearn_seed_start, unlearn_seed_end + 1):
        path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{train_seed}_unlearning_{method}_seed{unlearn_seed}_1000.pkl"
        try:
            with open(path, 'rb') as f:
                result = pickle.load(f)
                if hasattr(result, 'ndcg_server'):
                    results.append(result.ndcg_server[:1000])
        except FileNotFoundError:
            print(f"Warning: Unlearning file not found - {path}")
    
    return np.array(results) if results else None

def plot_scenario_results(base_dir, dataset, scenario, train_seed, 
                         unlearn_seed_start, unlearn_seed_end, save_dir):
    """Plot results for one scenario showing mean and variance"""
    models = ['Perfect', 'Navigational', 'Informational']
    methods = ['retrain', 'FedRemove', 'fedEraser', 'fineTuning', 'pga']
    
    sns.set_style("whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(36, 8))
    
    colors = {
        'retrain': 'green',
        'FedRemove': 'orange', 
        'fedEraser': 'red',
        'fineTuning': 'cyan',
        'pga': 'magenta'
    }
    
    for j, model in enumerate(models):
        ax = axes[j]
        
        # Plot training phase (single run)
        training_ndcg = load_training_result(base_dir, dataset, scenario, model, 1, train_seed)
        if training_ndcg is not None:
            epochs = np.arange(0, 1000)
            ax.plot(epochs, training_ndcg, 'b-', linewidth=2, label='Training', alpha=0.8)
        
        # Plot unlearning phase (multiple runs with mean and std)
        for method in methods:
            unlearn_results = load_unlearning_results(
                base_dir, dataset, scenario, model, 1, train_seed,
                unlearn_seed_start, unlearn_seed_end, method
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
                ax.plot(epochs, mean_ndcg, color=colors[method], 
                       linewidth=2.5, label=f'{method} (n={len(unlearn_results)})', zorder=2)
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
    save_path = os.path.join(save_dir, f"{dataset}_{scenario}_algorithm1.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved plot to {save_path}")

def print_final_metrics(base_dir, dataset, train_seed, unlearn_seed_start, unlearn_seed_end, save_dir):
    """Print final NDCG metrics with mean and std across unlearning seeds"""
    scenarios = ['clean', 'data_poison', 'model_poison']
    models = ['Perfect', 'Navigational', 'Informational']
    methods = ['retrain', 'FedRemove', 'fedEraser', 'fineTuning', 'pga']
    
    os.makedirs(save_dir, exist_ok=True)
    output_path = os.path.join(save_dir, f"{dataset}_algorithm1_summary.txt")
    
    with open(output_path, 'w') as f:
        header = f"Algorithm 1 Results: {dataset}\n"
        header += f"Training seed: {train_seed}\n"
        header += f"Unlearning seeds: {unlearn_seed_start}-{unlearn_seed_end}\n"
        header += "=" * 80 + "\n\n"
        f.write(header)
        print(header)
        
        for scenario in scenarios:
            section = f"\n{scenario.upper()} SCENARIO\n" + "-" * 80 + "\n"
            f.write(section)
            print(section)
            
            for model in models:
                f.write(f"\n{model} Model:\n")
                print(f"\n{model} Model:")
                
                # Get training final NDCG
                training_ndcg = load_training_result(base_dir, dataset, scenario, model, 1, train_seed)
                if training_ndcg is not None:
                    f.write(f"  Training final NDCG@10: {training_ndcg[-1]:.4f}\n")
                    print(f"  Training final NDCG@10: {training_ndcg[-1]:.4f}")
                
                f.write(f"  {'Method':<15} {'Mean':<10} {'Std':<10} {'Min':<10} {'Max':<10}\n")
                print(f"  {'Method':<15} {'Mean':<10} {'Std':<10} {'Min':<10} {'Max':<10}")
                
                for method in methods:
                    unlearn_results = load_unlearning_results(
                        base_dir, dataset, scenario, model, 1, train_seed,
                        unlearn_seed_start, unlearn_seed_end, method
                    )
                    
                    if unlearn_results is not None and len(unlearn_results) > 0:
                        final_ndcgs = unlearn_results[:, -1]  # Last epoch of each run
                        mean_val = np.mean(final_ndcgs)
                        std_val = np.std(final_ndcgs)
                        min_val = np.min(final_ndcgs)
                        max_val = np.max(final_ndcgs)
                        
                        line = f"  {method:<15} {mean_val:<10.4f} {std_val:<10.4f} {min_val:<10.4f} {max_val:<10.4f}\n"
                        f.write(line)
                        print(line.rstrip())
    
    print(f"\nSummary saved to {output_path}")

def calculate_w2_distances_final(base_dir, dataset, scenario, model, fold, train_seed,
                                 unlearn_seed_start, unlearn_seed_end, methods):
    """Calculate W2 distances on final NDCG values (Option 1)"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    # Load retrain results (gold standard)
    retrain_finals = []
    for unlearn_seed in range(unlearn_seed_start, unlearn_seed_end + 1):
        path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{train_seed}_unlearning_retrain_seed{unlearn_seed}_1000.pkl"
        try:
            with open(path, 'rb') as f:
                result = pickle.load(f)
                if hasattr(result, 'ndcg_server'):
                    retrain_finals.append(result.ndcg_server[-1])  # Final NDCG
        except FileNotFoundError:
            pass
    
    if len(retrain_finals) == 0:
        return None
    
    retrain_finals = np.array(retrain_finals)
    w2_distances = {}
    
    # Calculate W2 for each method
    for method in methods:
        if method == 'retrain':
            w2_distances[method] = 0.0  # W2 to itself is 0
            continue
            
        method_finals = []
        for unlearn_seed in range(unlearn_seed_start, unlearn_seed_end + 1):
            path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{train_seed}_unlearning_{method}_seed{unlearn_seed}_1000.pkl"
            try:
                with open(path, 'rb') as f:
                    result = pickle.load(f)
                    if hasattr(result, 'ndcg_server'):
                        method_finals.append(result.ndcg_server[-1])
            except FileNotFoundError:
                pass
        
        if len(method_finals) > 0:
            method_finals = np.array(method_finals)
            w2_distances[method] = wasserstein_2_distance(retrain_finals, method_finals)
    
    return w2_distances

def calculate_w2_trajectory(base_dir, dataset, scenario, model, fold, train_seed,
                           unlearn_seed_start, unlearn_seed_end, methods):
    """Calculate W2 distances over time (Option 2)"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    # Load retrain trajectories
    retrain_results = []
    for unlearn_seed in range(unlearn_seed_start, unlearn_seed_end + 1):
        path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{train_seed}_unlearning_retrain_seed{unlearn_seed}_1000.pkl"
        try:
            with open(path, 'rb') as f:
                result = pickle.load(f)
                if hasattr(result, 'ndcg_server'):
                    retrain_results.append(result.ndcg_server[:1000])
        except FileNotFoundError:
            pass
    
    if len(retrain_results) == 0:
        return None
    
    retrain_results = np.array(retrain_results)  # Shape: (n_seeds, 1000)
    w2_trajectories = {}
    
    # Calculate W2 at each epoch for each method
    for method in methods:
        if method == 'retrain':
            w2_trajectories[method] = np.zeros(1000)
            continue
        
        method_results = []
        for unlearn_seed in range(unlearn_seed_start, unlearn_seed_end + 1):
            path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{train_seed}_unlearning_{method}_seed{unlearn_seed}_1000.pkl"
            try:
                with open(path, 'rb') as f:
                    result = pickle.load(f)
                    if hasattr(result, 'ndcg_server'):
                        method_results.append(result.ndcg_server[:1000])
            except FileNotFoundError:
                pass
        
        if len(method_results) > 0:
            method_results = np.array(method_results)  # Shape: (n_seeds, 1000)
            w2_over_time = []
            
            for epoch in range(1000):
                w2 = wasserstein_2_distance(retrain_results[:, epoch], method_results[:, epoch])
                w2_over_time.append(w2)
            
            w2_trajectories[method] = np.array(w2_over_time)
    
    return w2_trajectories

def print_w2_analysis(base_dir, dataset, train_seed, unlearn_seed_start, unlearn_seed_end, save_dir):
    """Print W2 distance analysis comparing methods to retrain"""
    scenarios = ['clean', 'data_poison', 'model_poison']
    models = ['Perfect', 'Navigational', 'Informational']
    methods = ['retrain', 'FedRemove', 'fedEraser', 'fineTuning', 'pga']
    
    os.makedirs(save_dir, exist_ok=True)
    output_path = os.path.join(save_dir, f"{dataset}_algorithm1_w2_distances.txt")
    
    with open(output_path, 'w') as f:
        header = f"Wasserstein-2 Distance Analysis (Algorithm 1)\n"
        header += f"Dataset: {dataset}\n"
        header += f"Training seed: {train_seed}\n"
        header += f"Unlearning seeds: {unlearn_seed_start}-{unlearn_seed_end}\n"
        header += f"Reference: retrain (gold standard)\n"
        header += "=" * 80 + "\n\n"
        f.write(header)
        print(header)
        
        for scenario in scenarios:
            section = f"\n{scenario.upper()} SCENARIO\n" + "-" * 80 + "\n"
            f.write(section)
            print(section)
            
            for model in models:
                w2_distances = calculate_w2_distances_final(
                    base_dir, dataset, scenario, model, 1, train_seed,
                    unlearn_seed_start, unlearn_seed_end, methods
                )
                
                if w2_distances:
                    f.write(f"\n{model} Model:\n")
                    print(f"\n{model} Model:")
                    
                    f.write(f"  {'Method':<15} {'W2 Distance':<15} {'Interpretation':<30}\n")
                    print(f"  {'Method':<15} {'W2 Distance':<15} {'Interpretation':<30}")
                    
                    for method in methods:
                        if method in w2_distances:
                            w2 = w2_distances[method]
                            
                            # Interpretation thresholds
                            if w2 < 0.001:
                                interp = "Negligible difference"
                            elif w2 < 0.01:
                                interp = "Small difference"
                            elif w2 < 0.05:
                                interp = "Moderate difference"
                            else:
                                interp = "LARGE DIFFERENCE (Failure?)"
                            
                            line = f"  {method:<15} {w2:<15.6f} {interp:<30}\n"
                            f.write(line)
                            print(line.rstrip())
        
        # Summary statistics
        summary = "\n\n" + "=" * 80 + "\n"
        summary += "SUMMARY: Average W2 Distances Across Models\n"
        summary += "=" * 80 + "\n\n"
        f.write(summary)
        print(summary)
        
        for scenario in scenarios:
            f.write(f"{scenario.upper()}:\n")
            print(f"{scenario.upper()}:")
            
            avg_w2 = {}
            for method in methods:
                if method == 'retrain':
                    continue
                distances = []
                for model in models:
                    w2_distances = calculate_w2_distances_final(
                        base_dir, dataset, scenario, model, 1, train_seed,
                        unlearn_seed_start, unlearn_seed_end, methods
                    )
                    if w2_distances and method in w2_distances:
                        distances.append(w2_distances[method])
                
                if distances:
                    avg_w2[method] = np.mean(distances)
            
            # Sort by W2 distance
            sorted_methods = sorted(avg_w2.items(), key=lambda x: x[1])
            for method, w2 in sorted_methods:
                line = f"  {method:<15} {w2:<15.6f}\n"
                f.write(line)
                print(line.rstrip())
            f.write("\n")
            print()
    
    print(f"\nW2 distance analysis saved to {output_path}")

def plot_w2_trajectories(base_dir, dataset, scenario, train_seed, unlearn_seed_start, 
                        unlearn_seed_end, save_dir):
    """Plot W2 distance evolution over time"""
    models = ['Perfect', 'Navigational', 'Informational']
    methods = ['FedRemove', 'fedEraser', 'fineTuning', 'pga']  # Exclude retrain (always 0)
    
    sns.set_style("whitegrid")
    fig, axes = plt.subplots(1, 3, figsize=(36, 8))
    
    colors = {
        'FedRemove': 'orange',
        'fedEraser': 'red',
        'fineTuning': 'cyan',
        'pga': 'magenta'
    }
    
    for j, model in enumerate(models):
        ax = axes[j]
        
        w2_trajectories = calculate_w2_trajectory(
            base_dir, dataset, scenario, model, 1, train_seed,
            unlearn_seed_start, unlearn_seed_end, methods + ['retrain']
        )
        
        if w2_trajectories:
            epochs = np.arange(0, 1000)
            
            for method in methods:
                if method in w2_trajectories:
                    ax.plot(epochs, w2_trajectories[method], color=colors[method],
                           linewidth=2.5, label=method, alpha=0.8)
            
            # Add threshold lines for interpretation
            ax.axhline(y=0.01, color='green', linestyle='--', alpha=0.3, linewidth=1.5, 
                      label='Small difference')
            ax.axhline(y=0.05, color='orange', linestyle='--', alpha=0.3, linewidth=1.5,
                      label='Moderate difference')
        
        ax.set_title(f'{model}', fontsize=28, fontweight='bold')
        ax.set_xlabel('Unlearning Epoch', fontsize=24, fontweight='bold')
        ax.set_ylabel('W2 Distance from Retrain', fontsize=24, fontweight='bold')
        ax.tick_params(axis='both', which='major', labelsize=20)
        ax.grid(True, alpha=0.3)
        ax.set_ylim(bottom=0)
    
    # Single legend for all subplots
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, 1.08),
              fontsize=24, ncol=6, frameon=True, shadow=True)
    
    plt.suptitle(f'{scenario.replace("_", " ").title()} - W2 Distance Evolution', 
                 fontsize=32, fontweight='bold', y=1.12)
    plt.tight_layout()
    
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, f"{dataset}_{scenario}_algorithm1_w2_trajectory.png")
    plt.savefig(save_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved W2 trajectory plot to {save_path}")

if __name__ == "__main__":
    args = parse_args()
    
    print(f"Evaluating Algorithm 1 results for {args.dataset}")
    print(f"Training seed: {args.train_seed}")
    print(f"Unlearning seeds: {args.unlearn_seed_start}-{args.unlearn_seed_end}")
    print("=" * 80)
    
    scenarios = ['clean', 'data_poison', 'model_poison']
    
    for scenario in scenarios:
        print(f"\nProcessing {scenario} scenario...")
        plot_scenario_results(args.base_dir, args.dataset, scenario, args.train_seed,
                            args.unlearn_seed_start, args.unlearn_seed_end, args.save_dir)
    
    print("\nGenerating summary statistics...")
    print_final_metrics(args.base_dir, args.dataset, args.train_seed,
                       args.unlearn_seed_start, args.unlearn_seed_end, args.save_dir)
    
    print("\n" + "=" * 80)
    print("Computing Wasserstein-2 distances...")
    print("=" * 80)
    print_w2_analysis(args.base_dir, args.dataset, args.train_seed,
                     args.unlearn_seed_start, args.unlearn_seed_end, args.save_dir)
    
    print("\nGenerating W2 trajectory plots...")
    for scenario in scenarios:
        print(f"  Plotting {scenario}...")
        plot_w2_trajectories(args.base_dir, args.dataset, scenario, args.train_seed,
                           args.unlearn_seed_start, args.unlearn_seed_end, args.save_dir)
    
    print("\n" + "=" * 80)
    print("Evaluation complete!")

