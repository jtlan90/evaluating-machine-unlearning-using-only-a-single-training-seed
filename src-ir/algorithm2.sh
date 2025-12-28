#!/bin/bash
# Algorithm 2: Test PRE-TRAINING variance with CORRESPONDING unlearning seeds  
# - Pre-train 10 DIFFERENT models (seeds 1-10)
# - Run ONE unlearning experiment per model using the SAME seed
# - This isolates variance from the pre-training process
# Usage: ./algorithm2.sh

#set -e # uncomment to make the script stop when an error occurs; otherwise will ignore

# TODO: Adjust seed ranges and dataset paths if needed
SEED_START=1
SEED_END=10

echo "=============================================="
echo "Algorithm 2: Testing Pre-training Variance"
echo "Training seed range: $SEED_START to $SEED_END"
echo "Each training seed has matching unlearning seed"
echo "=============================================="

for seed in $(seq $SEED_START $SEED_END)
do
    echo ""
    echo "=========================================="
    echo "Experiment with seed: $seed"
    echo "Training with seed $seed, then unlearning with seed $seed"
    echo "=========================================="
    
    cd runs
    
    # STEP 1: Train with this seed
    echo ""
    echo "--- Training with seed $seed ---"
    
    # MQ2007 - All scenarios
    echo "Training MQ2007..."
    python train.py --dataset MQ2007 --scenario clean --seed $seed --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True
    python train.py --dataset MQ2007 --scenario data_poison --seed $seed --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    python train.py --dataset MQ2007 --scenario model_poison --seed $seed --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    
    # MSLR10K - Disabled (takes too long)
    # echo "Training MSLR10K..."
    # python train.py --dataset MSLR10K --scenario clean --seed $seed --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True
    # python train.py --dataset MSLR10K --scenario data_poison --seed $seed --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    # python train.py --dataset MSLR10K --scenario model_poison --seed $seed --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    
    # STEP 2: Unlearn using the SAME seed
    echo ""
    echo "--- Unlearning with seed $seed (from training seed $seed) ---"
    
    # MQ2007 - All scenarios and all unlearning methods
    echo "MQ2007 unlearning..."
    for scenario in clean data_poison model_poison
    do
        echo "  Scenario: $scenario"
        for method in retrain FedRemove fedEraser fineTuning pga
        do
            echo "    Method: $method"
            python unlearn.py --dataset MQ2007 --scenario $scenario --train_seed $seed --unlearn_seed $seed --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
        done
    done
    
    # MSLR10K - Disabled (takes too long)
    # echo "MSLR10K unlearning..."
    # for scenario in clean data_poison model_poison
    # do
    #     echo "  Scenario: $scenario"
    #     for method in retrain FedRemove fedEraser fineTuning pga
    #     do
    #         echo "    Method: $method"
    #         python unlearn.py --dataset MSLR10K --scenario $scenario --train_seed $seed --unlearn_seed $seed --unlearn_method $method --n_clients 10 --interactions_per_feedback 5 --interactions_budget 50000 --learning_rate 0.1 --update True --n_malicious 3
    #     done
    # done
    
    cd ..
    
    echo "Completed seed $seed (training + unlearning)"
done

echo ""
echo "=========================================="
echo "Algorithm 2 completed!"
echo "Dataset: MQ2007 only (MSLR10K disabled)"
echo "Generated $(($SEED_END - $SEED_START + 1)) pre-trained models"
echo "with 1 unlearning run per model (matching seed)"
echo "=========================================="

