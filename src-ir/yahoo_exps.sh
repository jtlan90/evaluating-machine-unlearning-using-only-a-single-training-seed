#!/bin/bash
# Yahoo experiments for a given seed
# Usage: ./yahoo_exps.sh SEED

SEED=$1

if [ -z "$SEED" ]; then
    echo "Error: Please provide a seed value"
    echo "Usage: ./yahoo_exps.sh SEED"
    exit 1
fi

echo "=========================================="
echo "Yahoo Experiments with seed: $SEED"
echo "=========================================="

cd runs

# Clean scenario
echo "--- Training Yahoo Clean (seed $SEED) ---"
python train.py --dataset Yahoo --scenario clean --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True

echo "--- Unlearning Yahoo Clean ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset Yahoo --scenario clean --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

# Data poison scenario
echo "--- Training Yahoo Data Poison (seed $SEED) ---"
python train.py --dataset Yahoo --scenario data_poison --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

echo "--- Unlearning Yahoo Data Poison ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset Yahoo --scenario data_poison --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

# Model poison scenario
echo "--- Training Yahoo Model Poison (seed $SEED) ---"
python train.py --dataset Yahoo --scenario model_poison --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

echo "--- Unlearning Yahoo Model Poison ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset Yahoo --scenario model_poison --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

cd ..

echo "Yahoo experiments completed for seed $SEED"

