#!/bin/bash
# This is the main file to run all federated learning and unlearning experiments (Algorithm 2)
# Bash file to run different seeds across all datasets, scenarios, and unlearning methods
# Each seed includes both training and unlearning in sequence
# Usage: ./algorithm2.sh

#set -e # uncomment to make the script stop when an error occurs; otherwise will ignore

# TODO: Set the range for the number of seeds you want to run. Value is used as seed
# TODO: Adjust dataset paths in --dataset_root_dir if needed

echo "=== Running training and unlearning experiments with multiple seeds ==="

for value in {100..100}
do
    echo "=========================================="
    echo "Running experiments with seed: $value"
    echo "=========================================="
    
    # Run MQ2007 experiments
    ./mq2007_exps.sh $value
    
    # Run MSLR10K experiments
    ./mslr10k_exps.sh $value
    
    # Optional: Yahoo experiments (uncomment if dataset is available)
    # ./yahoo_exps.sh $value
    
    # Optional: istella-s experiments (uncomment if dataset is available)
    # ./istella_exps.sh $value
    
    echo "Completed seed $value (training + unlearning)"
    echo ""
done

echo "=========================================="
echo "All experiments completed!"
echo "=========================================="

