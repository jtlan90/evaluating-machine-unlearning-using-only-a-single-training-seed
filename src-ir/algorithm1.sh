#!/bin/bash
# Algorithm 1: Test UNLEARNING variance with FIXED pre-training
# - Pre-train ONE model with seed 1
# - Run 10 different unlearning experiments (seeds 100-109) on the SAME pre-trained model
# - This isolates variance from the unlearning process itself
# Usage: ./algorithm1.sh

#set -e # uncomment to make the script stop when an error occurs; otherwise will ignore

# TODO: Adjust seed ranges and dataset paths if needed
TRAIN_SEED=1
UNLEARN_SEED_START=100
UNLEARN_SEED_END=109

echo "=============================================="
echo "Algorithm 1: Testing Unlearning Variance"
echo "Fixed training seed: $TRAIN_SEED"
echo "Unlearning seed range: $UNLEARN_SEED_START to $UNLEARN_SEED_END"
echo "=============================================="

# STEP 1: Pre-train models with seed 1 (only once)
echo ""
echo "=== STEP 1: Pre-training models with seed $TRAIN_SEED ==="
cd runs

# MQ2007 - All scenarios
echo "Training MQ2007..."
python train.py --dataset MQ2007 --scenario clean --seed $TRAIN_SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True
python train.py --dataset MQ2007 --scenario data_poison --seed $TRAIN_SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
python train.py --dataset MQ2007 --scenario model_poison --seed $TRAIN_SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

# MSLR10K - Disabled (takes too long)
# echo "Training MSLR10K..."
# python train.py --dataset MSLR10K --scenario clean --seed $TRAIN_SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True
# python train.py --dataset MSLR10K --scenario data_poison --seed $TRAIN_SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
# python train.py --dataset MSLR10K --scenario model_poison --seed $TRAIN_SEED --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3

cd ..
echo "Pre-training completed!"

# STEP 2: Run unlearning experiments with different seeds on the SAME pre-trained model
echo ""
echo "=== STEP 2: Running unlearning experiments with multiple seeds ==="
for unlearn_seed in $(seq $UNLEARN_SEED_START $UNLEARN_SEED_END)
do
    echo ""
    echo "=========================================="
    echo "Unlearning experiment with seed: $unlearn_seed"
    echo "Using pre-trained model from seed: $TRAIN_SEED"
    echo "=========================================="
    
    cd runs
    
    # MQ2007 - All scenarios and all unlearning methods
    echo "--- MQ2007 Unlearning (unlearn_seed=$unlearn_seed) ---"
    for scenario in clean data_poison model_poison
    do
        echo "  Scenario: $scenario"
        for method in retrain FedRemove fedEraser fineTuning pga
        do
            echo "    Method: $method"
            python unlearn.py --dataset MQ2007 --scenario $scenario --train_seed $TRAIN_SEED --unlearn_seed $unlearn_seed --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
        done
    done
    
    # MSLR10K - Disabled (takes too long)
    # echo "--- MSLR10K Unlearning (unlearn_seed=$unlearn_seed) ---"
    # for scenario in clean data_poison model_poison
    # do
    #     echo "  Scenario: $scenario"
    #     for method in retrain FedRemove fedEraser fineTuning pga
    #     do
    #         echo "    Method: $method"
    #         python unlearn.py --dataset MSLR10K --scenario $scenario --train_seed $TRAIN_SEED --unlearn_seed $unlearn_seed --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    #     done
    # done
    
    cd ..
    echo "Completed unlearning with seed $unlearn_seed"
done

echo ""
echo "=========================================="
echo "Algorithm 1 completed!"
echo "Dataset: MQ2007 only (MSLR10K disabled)"
echo "Generated 1 pre-trained model (seed $TRAIN_SEED)"
echo "with $(($UNLEARN_SEED_END - $UNLEARN_SEED_START + 1)) unlearning runs per scenario/method"
echo "=========================================="

