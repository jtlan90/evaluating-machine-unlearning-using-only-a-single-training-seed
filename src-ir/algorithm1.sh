#!/bin/bash
# This is the main file to run all federated learning experiments (Algorithm 1)
# Bash file to run different seeds across all datasets and scenarios
# Usage: ./algorithm1.sh

#set -e # uncomment to make the script stop when an error occurs; otherwise will ignore

# TODO: Set the range for the number of seeds you want to run. Value is used as seed
# TODO: Adjust dataset paths in --dataset_root_dir if needed

# Pre-train (run initial training) for seed 1 on all datasets and scenarios
echo "=== Pre-training models with seed 1 ==="
cd runs

# MQ2007 - Clean scenario
python train.py --dataset MQ2007 --scenario clean --seed 1 --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True

# MQ2007 - Data poison scenario  
python train.py --dataset MQ2007 --scenario data_poison --seed 1 --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

# MQ2007 - Model poison scenario
python train.py --dataset MQ2007 --scenario model_poison --seed 1 --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

# MSLR10K - Clean scenario
python train.py --dataset MSLR10K --scenario clean --seed 1 --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True

# MSLR10K - Data poison scenario
python train.py --dataset MSLR10K --scenario data_poison --seed 1 --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

# MSLR10K - Model poison scenario
python train.py --dataset MSLR10K --scenario model_poison --seed 1 --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

cd ..

echo "=== Running experiments with multiple seeds ==="
# TODO: Set the range for the number of seeds you want to run
for value in {100..105}
do
    echo "=========================================="
    echo "Running experiments with seed: $value"
    echo "=========================================="
    
    # Run MQ2007 experiments (training only, no unlearning)
    cd runs
    python train.py --dataset MQ2007 --scenario clean --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True
    python train.py --dataset MQ2007 --scenario data_poison --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    python train.py --dataset MQ2007 --scenario model_poison --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    cd ..
    
    # Run MSLR10K experiments (training only, no unlearning)
    cd runs
    python train.py --dataset MSLR10K --scenario clean --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True
    python train.py --dataset MSLR10K --scenario data_poison --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    python train.py --dataset MSLR10K --scenario model_poison --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    cd ..
    
    # Optional: Yahoo experiments (uncomment if dataset is available)
    # cd runs
    # python train.py --dataset Yahoo --scenario clean --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True
    # python train.py --dataset Yahoo --scenario data_poison --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    # python train.py --dataset Yahoo --scenario model_poison --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    # cd ..
    
    # Optional: istella-s experiments (uncomment if dataset is available)
    # cd runs
    # python train.py --dataset istella-s --scenario clean --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True
    # python train.py --dataset istella-s --scenario data_poison --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    # python train.py --dataset istella-s --scenario model_poison --seed $value --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    # cd ..
    
    echo "Completed seed $value"
    echo ""
done

echo "=========================================="
echo "All training experiments completed!"
echo "=========================================="

