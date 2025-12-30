#!/bin/bash
# istella-s experiments for a given seed
# Usage: ./istella_exps.sh SEED

SEED=$1

if [ -z "$SEED" ]; then
    echo "Error: Please provide a seed value"
    echo "Usage: ./istella_exps.sh SEED"
    exit 1
fi

echo "=========================================="
echo "istella-s Experiments with seed: $SEED"
echo "=========================================="

cd runs

# Clean scenario
echo "--- Training istella-s Clean (seed $SEED) ---"
python train.py --dataset istella-s --scenario clean --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True

echo "--- Unlearning istella-s Clean ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset istella-s --scenario clean --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

# Data poison scenario
echo "--- Training istella-s Data Poison (seed $SEED) ---"
python train.py --dataset istella-s --scenario data_poison --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

echo "--- Unlearning istella-s Data Poison ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset istella-s --scenario data_poison --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

# Model poison scenario
echo "--- Training istella-s Model Poison (seed $SEED) ---"
python train.py --dataset istella-s --scenario model_poison --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

echo "--- Unlearning istella-s Model Poison ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset istella-s --scenario model_poison --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

cd ..

echo "istella-s experiments completed for seed $SEED"

