#!/usr/bin/env python3
"""
Compute pairwise W2 distances between different training seeds for each method.
This measures how much each method's performance distribution changes across pre-training seeds.
"""
import os
import sys
import pickle
import numpy as np
from scipy.stats import wasserstein_distance
from itertools import combinations

# Add project root to path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

def load_method_results(base_dir, dataset, scenario, model, fold, method, seeds):
    """Load results for a specific method across multiple training seeds"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    results = {}
    for seed in seeds:
        if method == 'training':
            path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{seed}_state_1000.pkl"
        else:
            path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{seed}_unlearning_{method}_seed{seed}_1000.pkl"
        
        try:
            with open(path, 'rb') as f:
                result = pickle.load(f)
                if hasattr(result, 'ndcg_server'):
                    results[seed] = result.ndcg_server[-1]  # Final NDCG
        except FileNotFoundError:
            pass
    
    return results

def compute_pairwise_w2(base_dir, dataset, seeds):
    """Compute pairwise W2 distances for all methods across training seeds"""
    
    scenarios = ['clean', 'data_poison', 'model_poison']
    models = ['Perfect', 'Navigational', 'Informational']
    methods = ['training', 'retrain', 'FedRemove', 'fedEraser', 'fineTuning', 'pga']
    
    output = []
    output.append("=" * 100)
    output.append("PAIRWISE W2 DISTANCES ACROSS PRE-TRAINING SEEDS")
    output.append("=" * 100)
    output.append("\nMeasures: How much does each method's performance change when starting from different pre-trained models?")
    output.append("Interpretation: Large W2 = method is highly sensitive to pre-training seed choice")
    output.append("")
    
    for scenario in scenarios:
        output.append("\n" + "=" * 100)
        output.append(f"{scenario.upper()} SCENARIO")
        output.append("=" * 100)
        
        for model in models:
            output.append(f"\n{model} Model:")
            output.append("-" * 100)
            
            for method in methods:
                # Load results for all seeds
                results_dict = load_method_results(base_dir, dataset, scenario, model, 1, method, seeds)
                
                if len(results_dict) < 2:
                    continue
                
                # Compute all pairwise W2 distances
                seed_pairs = list(combinations(sorted(results_dict.keys()), 2))
                w2_distances = []
                
                for seed1, seed2 in seed_pairs:
                    val1 = results_dict[seed1]
                    val2 = results_dict[seed2]
                    # W2 between two single values is just their absolute difference
                    w2 = abs(val1 - val2)
                    w2_distances.append(w2)
                
                if w2_distances:
                    mean_w2 = np.mean(w2_distances)
                    max_w2 = np.max(w2_distances)
                    min_w2 = np.min(w2_distances)
                    
                    # Interpretation
                    if mean_w2 < 0.01:
                        interp = "Low sensitivity"
                    elif mean_w2 < 0.05:
                        interp = "Moderate sensitivity"
                    else:
                        interp = "HIGH SENSITIVITY ⚠️"
                    
                    output.append(f"  {method:<15} Mean W2: {mean_w2:.6f}  Max: {max_w2:.6f}  Min: {min_w2:.6f}  [{interp}]")
            
            output.append("")
    
    # Summary statistics
    output.append("\n" + "=" * 100)
    output.append("SUMMARY: Average W2 Across Models (Mean of Pairwise Distances)")
    output.append("=" * 100)
    
    for scenario in scenarios:
        output.append(f"\n{scenario.upper()}:")
        
        method_averages = {}
        for method in methods:
            all_w2 = []
            for model in models:
                results_dict = load_method_results(base_dir, dataset, scenario, model, 1, method, seeds)
                if len(results_dict) >= 2:
                    seed_pairs = list(combinations(sorted(results_dict.keys()), 2))
                    for seed1, seed2 in seed_pairs:
                        w2 = abs(results_dict[seed1] - results_dict[seed2])
                        all_w2.append(w2)
            
            if all_w2:
                method_averages[method] = np.mean(all_w2)
        
        # Sort by W2 (ascending - least sensitive first)
        sorted_methods = sorted(method_averages.items(), key=lambda x: x[1])
        for method, avg_w2 in sorted_methods:
            if avg_w2 < 0.01:
                symbol = "✓"
            elif avg_w2 < 0.05:
                symbol = "⚠️"
            else:
                symbol = "🚨"
            output.append(f"  {method:<15} {avg_w2:.6f}  {symbol}")
    
    return "\n".join(output)

if __name__ == "__main__":
    base_dir = "../save"
    dataset = "MQ2007"
    seeds = list(range(1, 11))  # Seeds 1-10
    
    result = compute_pairwise_w2(base_dir, dataset, seeds)
    print(result)
    
    # Save to file
    output_path = "results/algorithm2/MQ2007_pairwise_w2_pretrain_sensitivity.txt"
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(result)
    
    print(f"\n\nResults saved to: {output_path}")

