#!/bin/bash
# MQ2007 experiments for a given seed
# Usage: ./mq2007_exps.sh SEED

SEED=$1

if [ -z "$SEED" ]; then
    echo "Error: Please provide a seed value"
    echo "Usage: ./mq2007_exps.sh SEED"
    exit 1
fi

echo "=========================================="
echo "MQ2007 Experiments with seed: $SEED"
echo "=========================================="

cd runs

# Clean scenario
echo "--- Training MQ2007 Clean (seed $SEED) ---"
python train.py --dataset MQ2007 --scenario clean --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True

echo "--- Unlearning MQ2007 Clean ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset MQ2007 --scenario clean --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

# Data poison scenario
echo "--- Training MQ2007 Data Poison (seed $SEED) ---"
python train.py --dataset MQ2007 --scenario data_poison --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

echo "--- Unlearning MQ2007 Data Poison ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset MQ2007 --scenario data_poison --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

# Model poison scenario
echo "--- Training MQ2007 Model Poison (seed $SEED) ---"
python train.py --dataset MQ2007 --scenario model_poison --seed $SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

echo "--- Unlearning MQ2007 Model Poison ---"
for method in retrain FedRemove fedEraser fineTuning pga
do
    echo "  Method: $method"
    python unlearn.py --dataset MQ2007 --scenario model_poison --seed $SEED --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
done

cd ..

echo "MQ2007 experiments completed for seed $SEED"

