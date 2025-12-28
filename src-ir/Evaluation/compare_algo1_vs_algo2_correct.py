#!/usr/bin/env python3
"""
Correct W2 comparison: Compute W2 distance BETWEEN Algorithm 1 and Algorithm 2 distributions
Following Lanyon et al. methodology exactly
"""
import os
import sys
import pickle
import numpy as np
import matplotlib.pyplot as plt

# Add project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

def wasserstein_2_distance(u, v):
    """Compute Wasserstein-2 distance"""
    u = np.asarray(u).flatten()
    v = np.asarray(v).flatten()
    u_sorted = np.sort(u)
    v_sorted = np.sort(v)
    if len(u) == len(v):
        return np.sqrt(np.mean((u_sorted - v_sorted)**2))
    else:
        n_u, n_v = len(u), len(v)
        all_quantiles = np.unique(np.concatenate([
            np.linspace(0, 1, n_u + 1),
            np.linspace(0, 1, n_v + 1)
        ]))
        u_quantiles = np.interp(all_quantiles, np.linspace(0, 1, n_u), u_sorted)
        v_quantiles = np.interp(all_quantiles, np.linspace(0, 1, n_v), v_sorted)
        return np.sqrt(np.trapz((u_quantiles - v_quantiles)**2, all_quantiles))

def load_algo1_final_results(base_dir, dataset, scenario, model, fold, train_seed, method, unlearn_seeds):
    """Load Algorithm 1 final NDCG values: fixed training seed, varying unlearning seeds"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    results = []
    for unlearn_seed in unlearn_seeds:
        path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{train_seed}_unlearning_{method}_seed{unlearn_seed}_1000.pkl"
        try:
            with open(path, 'rb') as f:
                result = pickle.load(f)
                if hasattr(result, 'ndcg_server'):
                    results.append(result.ndcg_server[-1])
        except FileNotFoundError:
            pass
    return np.array(results)

def load_algo2_final_results(base_dir, dataset, scenario, model, fold, method, train_seeds):
    """Load Algorithm 2 final NDCG values: varying training seeds with matching unlearning seeds"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    results = []
    for train_seed in train_seeds:
        path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{train_seed}_unlearning_{method}_seed{train_seed}_1000.pkl"
        try:
            with open(path, 'rb') as f:
                result = pickle.load(f)
                if hasattr(result, 'ndcg_server'):
                    results.append(result.ndcg_server[-1])
        except FileNotFoundError:
            pass
    return np.array(results)

def compute_w2_between_algorithms(base_dir, dataset, scenarios, models, methods, 
                                  train_seed_algo1, unlearn_seeds_algo1, train_seeds_algo2):
    """
    Compute W2 distance BETWEEN Algorithm 1 and Algorithm 2 distributions for each method
    This is what Lanyon et al. do: wasserstein1d(algorithm_1_results, algorithm_2_results, p = 2)
    """
    results = {}
    
    for scenario in scenarios:
        results[scenario] = {}
        for model in models:
            results[scenario][model] = {}
            
            for method in methods:
                # Get Algorithm 1 distribution (10 unlearning seeds)
                algo1_dist = load_algo1_final_results(
                    base_dir, dataset, scenario, model, 1, 
                    train_seed_algo1, method, unlearn_seeds_algo1
                )
                
                # Get Algorithm 2 distribution (10 training seeds)
                algo2_dist = load_algo2_final_results(
                    base_dir, dataset, scenario, model, 1,
                    method, train_seeds_algo2
                )
                
                # Compute W2 distance BETWEEN the two distributions
                if len(algo1_dist) > 0 and len(algo2_dist) > 0:
                    w2 = wasserstein_2_distance(algo1_dist, algo2_dist)
                    results[scenario][model][method] = {
                        'w2': w2,
                        'algo1_mean': np.mean(algo1_dist),
                        'algo1_std': np.std(algo1_dist),
                        'algo2_mean': np.mean(algo2_dist),
                        'algo2_std': np.std(algo2_dist),
                        'n_algo1': len(algo1_dist),
                        'n_algo2': len(algo2_dist)
                    }
    
    return results

# Main computation
base_dir = "../save"
dataset = "MQ2007"
scenarios = ['clean', 'data_poison', 'model_poison']
models = ['Perfect', 'Navigational', 'Informational']
methods = ['retrain', 'FedRemove', 'fedEraser', 'fineTuning', 'pga']
method_labels = {'retrain': 'Retrain', 'FedRemove': 'FedRemove', 
                'fedEraser': 'FedEraser', 'fineTuning': 'FineTuning', 'pga': 'PGA'}

train_seed_algo1 = 1
unlearn_seeds_algo1 = list(range(100, 110))
train_seeds_algo2 = list(range(1, 11))

print("="*100)
print("CORRECT W2 COMPARISON: Algorithm 1 vs Algorithm 2")
print("Following Lanyon et al. methodology")
print("="*100)
print("\nFor each method, compute W2 distance BETWEEN:")
print("  - Algorithm 1 distribution (fixed train seed, 10 unlearning seeds)")
print("  - Algorithm 2 distribution (10 training seeds, matching unlearning seeds)")
print("\nInterpretation:")
print("  - High W2 = Evaluation protocol choice significantly affects results")
print("  - Low W2 = Method robust to evaluation protocol")
print("="*100)

results = compute_w2_between_algorithms(
    base_dir, dataset, scenarios, models, methods,
    train_seed_algo1, unlearn_seeds_algo1, train_seeds_algo2
)

# Print detailed results
output = []
for scenario in scenarios:
    output.append(f"\n{'='*100}")
    output.append(f"{scenario.upper()} SCENARIO")
    output.append(f"{'='*100}\n")
    
    for model in models:
        output.append(f"{model} Model:")
        output.append(f"{'-'*100}")
        output.append(f"{'Method':<15} {'W2 Distance':<15} {'Algo1 Mean±Std':<25} {'Algo2 Mean±Std':<25} {'Interpretation'}")
        output.append(f"{'-'*100}")
        
        for method in methods:
            if method in results[scenario][model]:
                r = results[scenario][model][method]
                w2 = r['w2']
                
                if w2 < 0.01:
                    interp = "Negligible difference"
                elif w2 < 0.05:
                    interp = "Small difference"
                elif w2 < 0.1:
                    interp = "Moderate difference"
                else:
                    interp = "LARGE DIFFERENCE 🚨"
                
                algo1_str = f"{r['algo1_mean']:.4f}±{r['algo1_std']:.4f}"
                algo2_str = f"{r['algo2_mean']:.4f}±{r['algo2_std']:.4f}"
                
                output.append(f"{method:<15} {w2:<15.6f} {algo1_str:<25} {algo2_str:<25} {interp}")
        
        output.append("")

# Compute average across models
output.append(f"\n{'='*100}")
output.append(f"SUMMARY: Average W2 Distance Across Models")
output.append(f"{'='*100}\n")

for scenario in scenarios:
    output.append(f"{scenario.upper()}:")
    output.append(f"{'Method':<15} {'Mean W2':<15} {'Interpretation'}")
    output.append(f"{'-'*80}")
    
    method_w2s = {method: [] for method in methods}
    for model in models:
        for method in methods:
            if method in results[scenario][model]:
                method_w2s[method].append(results[scenario][model][method]['w2'])
    
    # Sort by W2 distance
    method_avg_w2 = [(method, np.mean(w2s)) for method, w2s in method_w2s.items() if len(w2s) > 0]
    method_avg_w2.sort(key=lambda x: x[1])
    
    for method, avg_w2 in method_avg_w2:
        if avg_w2 < 0.01:
            symbol = "✓ Robust"
        elif avg_w2 < 0.05:
            symbol = "⚠️ Moderate"
        else:
            symbol = "🚨 High sensitivity"
        
        output.append(f"{method:<15} {avg_w2:<15.6f} {symbol}")
    
    output.append("")

result_text = "\n".join(output)
print(result_text)

# Save
output_path = "results/CORRECT_ALGO1_VS_ALGO2_W2.txt"
os.makedirs(os.path.dirname(output_path), exist_ok=True)
with open(output_path, 'w') as f:
    f.write(result_text)

print(f"\n\nResults saved to: {output_path}")

# Generate visualization
print("\nGenerating visualization...")

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Wasserstein-2 Distance Between Algorithm 1 and Algorithm 2\n' + 
             'Higher W2 = Evaluation protocol choice affects method performance',
             fontsize=16, fontweight='bold', y=1.02)

scenario_titles = {
    'clean': 'Clean Scenario',
    'data_poison': 'Data Poisoning',
    'model_poison': 'Model Poisoning'
}

colors = {
    'retrain': '#3498db',
    'FedRemove': '#e74c3c',
    'fedEraser': '#2ecc71',
    'fineTuning': '#f39c12',
    'pga': '#9b59b6'
}

for idx, scenario in enumerate(scenarios):
    ax = axes[idx]
    
    # Compute average W2 across models for each method
    method_w2s = []
    method_names = []
    method_colors = []
    
    for method in methods:
        w2_values = []
        for model in models:
            if method in results[scenario][model]:
                w2_values.append(results[scenario][model][method]['w2'])
        
        if w2_values:
            method_w2s.append(np.mean(w2_values))
            method_names.append(method_labels[method])
            method_colors.append(colors[method])
    
    # Create bar chart
    x = np.arange(len(method_names))
    bars = ax.bar(x, method_w2s, color=method_colors, alpha=0.8, 
                  edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for i, (bar, w2) in enumerate(zip(bars, method_w2s)):
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height + 0.002,
                f'{w2:.4f}', ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Add threshold lines
    ax.axhline(y=0.01, color='green', linestyle='--', alpha=0.5, linewidth=1.5, label='Negligible (0.01)')
    ax.axhline(y=0.05, color='orange', linestyle='--', alpha=0.5, linewidth=1.5, label='Moderate (0.05)')
    ax.axhline(y=0.1, color='red', linestyle='--', alpha=0.5, linewidth=1.5, label='Large (0.1)')
    
    ax.set_xlabel('Method', fontsize=12, fontweight='bold')
    ax.set_ylabel('W2 Distance\n(Algo1 vs Algo2)', fontsize=12, fontweight='bold')
    ax.set_title(scenario_titles[scenario], fontsize=14, fontweight='bold', pad=10)
    ax.set_xticks(x)
    ax.set_xticklabels(method_names, rotation=15, ha='right')
    ax.grid(axis='y', alpha=0.3, linestyle='--')
    
    if idx == 2:
        ax.legend(loc='upper left', fontsize=9)
    
    # Highlight FedRemove
    fedremove_idx = methods.index('FedRemove')
    ax.axvspan(fedremove_idx - 0.4, fedremove_idx + 0.4, alpha=0.1, color='red', zorder=-1)

plt.tight_layout()

output_path_png = "results/CORRECT_ALGO1_VS_ALGO2_W2.png"
plt.savefig(output_path_png, dpi=300, bbox_inches='tight')
print(f"✅ Visualization saved: {output_path_png}")

plt.show()

print("\n" + "="*100)
print("✅ CORRECT W2 ANALYSIS COMPLETE")
print("="*100)
print("\nKey difference from previous analysis:")
print("  OLD: Computed W2 within each algorithm (pairwise distances)")
print("  NEW: Computed W2 BETWEEN algorithms (distribution difference)")
print("\nThis matches Lanyon et al. methodology exactly!")

