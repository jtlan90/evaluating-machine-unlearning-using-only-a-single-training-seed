#!/usr/bin/env python3
"""
Export experiment results to CSV for R analysis
"""
import os
import sys
import pickle
import pandas as pd
import numpy as np

# Add project root
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(current_dir, ".."))
sys.path.append(project_root)

def load_results(base_dir, dataset, scenario, model, fold, train_seed, method, unlearn_seed):
    """Load a single result file"""
    scenario_map = {'clean': 'clean', 'data_poison': 'data', 'model_poison': 'model'}
    scenario_dir = scenario_map[scenario]
    
    path = f"{base_dir}/{dataset}/{fold}/{scenario_dir}/{model}_training_seed{train_seed}_unlearning_{method}_seed{unlearn_seed}_1000.pkl"
    try:
        with open(path, 'rb') as f:
            result = pickle.load(f)
            if hasattr(result, 'ndcg_server'):
                return result.ndcg_server[-1]  # Final NDCG value
    except FileNotFoundError:
        pass
    return None

# Configuration
base_dir = "../save"
dataset = "MQ2007"
scenarios = ['clean', 'data_poison', 'model_poison']
models = ['Perfect', 'Navigational', 'Informational']
methods = ['retrain', 'FedRemove', 'fedEraser', 'fineTuning', 'pga']

# Algorithm 1: Fixed training seed, varying unlearning seeds
train_seed_algo1 = 1
unlearn_seeds_algo1 = list(range(100, 110))

# Algorithm 2: Varying training seeds with matching unlearning seeds
train_seeds_algo2 = list(range(1, 11))

# Collect all results
data = []

print("Exporting Algorithm 1 results...")
for scenario in scenarios:
    for model in models:
        for method in methods:
            for unlearn_seed in unlearn_seeds_algo1:
                ndcg = load_results(base_dir, dataset, scenario, model, 1, 
                                   train_seed_algo1, method, unlearn_seed)
                if ndcg is not None:
                    data.append({
                        'algorithm': 1,
                        'scenario': scenario,
                        'model': model,
                        'method': method,
                        'train_seed': train_seed_algo1,
                        'unlearn_seed': unlearn_seed,
                        'ndcg': ndcg
                    })

print("Exporting Algorithm 2 results...")
for scenario in scenarios:
    for model in models:
        for method in methods:
            for train_seed in train_seeds_algo2:
                ndcg = load_results(base_dir, dataset, scenario, model, 1,
                                   train_seed, method, train_seed)
                if ndcg is not None:
                    data.append({
                        'algorithm': 2,
                        'scenario': scenario,
                        'model': model,
                        'method': method,
                        'train_seed': train_seed,
                        'unlearn_seed': train_seed,
                        'ndcg': ndcg
                    })

# Create DataFrame
df = pd.DataFrame(data)

# Save to CSV
output_dir = "results/data"
os.makedirs(output_dir, exist_ok=True)
output_file = f"{output_dir}/MQ2007_all_results.csv"
df.to_csv(output_file, index=False)

print(f"\n✅ Exported {len(df)} results to: {output_file}")
print(f"\nDataFrame shape: {df.shape}")
print(f"\nColumns: {df.columns.tolist()}")
print(f"\nFirst few rows:")
print(df.head(10))
print(f"\nResults by algorithm:")
print(df['algorithm'].value_counts())
