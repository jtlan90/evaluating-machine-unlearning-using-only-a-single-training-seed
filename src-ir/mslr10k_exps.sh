#!/bin/bash
# MSLR10K experiments for a given seed
# Usage: ./mslr10k_exps.sh SEED

SEED=$1

if [ -z "$SEED" ]; then
    echo "Error: Please provide a seed value"
    echo "Usage: ./mslr10k_exps.sh SEED"
    exit 1
fi

echo "=========================================="
echo "MSLR10K Experiments with seed: $SEED"
echo "=========================================="

cd runs

# Clean scenario
echo "--- Training MSLR10K Clean (seed $SEED) ---"
python train.py --dataset MSLR10K --scenario clean --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True

echo "--- Unlearning MSLR10K Clean ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset MSLR10K --scenario clean --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

# Data poison scenario
echo "--- Training MSLR10K Data Poison (seed $SEED) ---"
python train.py --dataset MSLR10K --scenario data_poison --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

echo "--- Unlearning MSLR10K Data Poison ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset MSLR10K --scenario data_poison --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

# Model poison scenario
echo "--- Training MSLR10K Model Poison (seed $SEED) ---"
python train.py --dataset MSLR10K --scenario model_poison --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

echo "--- Unlearning MSLR10K Model Poison ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset MSLR10K --scenario model_poison --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

cd ..

echo "MSLR10K experiments completed for seed $SEED"

