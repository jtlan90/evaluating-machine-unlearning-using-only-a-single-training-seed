# Unlearning for Federated Online Learning to Rank

## News
- 🔥Our paper has been accepted by SIGIR2025!

## Overview

This repository implements and evaluates machine unlearning methods for Federated Online Learning to Rank (FOLTR). The codebase includes:

- **Training**: Federated learning with multiple clients and click models
- **Poisoning Scenarios**: Clean, data poisoning, and model poisoning
- **Unlearning Methods**: retrain, FedRemove, fedEraser, fineTuning, PGA
- **Variance Analysis**: Two experimental designs to isolate variance sources:
  - **Algorithm 1**: Fixed pre-training + multiple unlearning runs
  - **Algorithm 2**: Multiple pre-training runs + matched unlearning runs
- **Comprehensive Evaluation**: Statistical analysis and visualization of results

## Download datasets
In the paper, we use four popular LTR datasets: MQ2007, MSLR-WEB10K, Yahoo! and Istella-S.
- MQ2007 can be downloaded from the Microsoft Research [website](https://www.microsoft.com/en-us/research/project/letor-learning-rank-information-retrieval/). 
- MSLR-WEB10K can be downloaded from the Microsoft Research [website](https://www.microsoft.com/en-us/research/project/mslr/).  
- Yahoo! can be downloaded from [Yahoo Webscope program](https://webscope.sandbox.yahoo.com/catalog.php?datatype=c).
- Istella-S can be downloaded from [Instella-S website](https://istella.ai/datasets/letor-dataset/)

After downloading data files, they have to be unpacked within the `./datasets` folder.

**Important:** The MSLR-WEB10K folder should be renamed to `MSLR10K` after unpacking:
```bash
cd datasets
mv MSLR-WEB10K MSLR10K
```


## Environment Setups

### Quick Setup
Run the setup script to create the conda environment:
```bash
./setup_env.sh
conda activate foltr
pip install -r requirements.txt
```

### Manual Setup
- Create a new virtual environment:
``` bash
conda create --name foltr python=3.8.13
```

- Install all the libraries for running the code:
``` bash
pip install -r requirements.txt
```

## Running Experiments

### Automated Experiment Scripts

Two main bash scripts are provided for investigating different sources of variance in machine unlearning:

#### Algorithm 1: Testing Unlearning Variance
```bash
./algorithm1.sh
```
**Purpose:** Isolate variance from the unlearning process itself

**Design:**
- Pre-trains **ONE** model with seed 1 (fixed)
- Runs **10 unlearning experiments** with seeds 100-109 on the SAME pre-trained model
- All unlearning methods: retrain, FedRemove, fedEraser, fineTuning, pga
- Datasets: MQ2007, MSLR10K (Yahoo and istella-s optional)

**Key insight:** If results vary across unlearning seeds, the unlearning method is sensitive to random initialization.

To customize seed ranges, edit `TRAIN_SEED`, `UNLEARN_SEED_START`, and `UNLEARN_SEED_END` in `algorithm1.sh`.

#### Algorithm 2: Testing Pre-training Variance
```bash
./algorithm2.sh
```
**Purpose:** Isolate variance from the pre-training process

**Design:**
- Pre-trains **10 DIFFERENT** models with seeds 1-10
- Runs **ONE unlearning experiment** per model using the SAME seed
- All unlearning methods: retrain, FedRemove, fedEraser, fineTuning, pga
- Datasets: MQ2007, MSLR10K (Yahoo and istella-s optional)

**Key insight:** If results vary across training seeds, pre-training randomness dominates performance.

To customize seed ranges, edit `SEED_START` and `SEED_END` in `algorithm2.sh`.

#### Quick Comparison

| Aspect | Algorithm 1 | Algorithm 2 |
|--------|-------------|-------------|
| **Pre-training Seeds** | 1 (fixed) | 1-10 (varies) |
| **Unlearning Seeds** | 100-109 (varies) | 1-10 (matches training) |
| **# of Pre-trained Models** | 1 | 10 |
| **# of Unlearning Runs** | 10 per scenario/method | 1 per scenario/method |
| **Measures Variance From** | Unlearning process | Pre-training process |
| **Use Case** | Test unlearning stability | Test pre-training impact |

**Example:**
- **Algorithm 1**: Train once with seed 1 → Unlearn 10 times (seeds 100-109) → See if unlearning is consistent
- **Algorithm 2**: Train 10 times (seeds 1-10) → Unlearn once each (matching seeds) → See if pre-training matters

### Individual Dataset Scripts (Legacy)

For manual control, you can run experiments for individual datasets with a single seed:

```bash
./mq2007_exps.sh SEED      # Run all MQ2007 experiments for a given seed
./mslr10k_exps.sh SEED     # Run all MSLR10K experiments for a given seed
./yahoo_exps.sh SEED       # Run all Yahoo experiments for a given seed
./istella_exps.sh SEED     # Run all istella-s experiments for a given seed
```

Each script uses the **same seed for both training and unlearning** (equivalent to Algorithm 2 behavior for a single seed).

**Note:** These scripts use the legacy `--seed` parameter which works via backward compatibility. For more control over training vs unlearning seeds, use Algorithm 1 or Algorithm 2 scripts, or run `train.py` and `unlearn.py` manually with `--train_seed` and `--unlearn_seed` parameters.

### Troubleshooting

If you encounter line ending issues (especially on Windows), run:
```bash
./dos2unix.sh
```

## Running Federated Learning Process (Manual)
For manual control, the experiment is divided into two parts: first, the Federated Learning phase needs to be conducted, followed by the implementation of Federated Unlearning.

### Basic Usage
Run the script with the default parameters:
```bash
cd runs
python train.py
```
This command trains the model using the `MQ2007` dataset with default settings, saving results to the `../save` directory.


### Complete Parameter Example

To customize the training, you can pass arguments to the script. Below is an example of running the script with all available parameters:
```bash
cd runs
python train.py \
  --dataset MQ2007 \
  --n_clients 10 \
  --interactions_per_feedback 5 \
  --interactions_budget 50000 \
  --learning_rate 0.1 \
  --update True \
  --num_update 50 \
  --seed 1 \
  --scenario CLEAN \
  --n_malicious 3 \
  --dataset_root_dir ../datasets \
  --save_dir ../save
```

### Click Models

Click models simulate user behavior based on relevance scores. The codebase supports the following click models:

- `Perfect`
- `Navigational`
- `Informational`
- `Poison` (only used in `data_poison` scenarios)

Click model configurations vary based on the dataset. Refer to the `get_click_model` function in the code for details.

### Training Output

After training, results will be saved in a `.pkl` file in the specified `save_dir`.

Example file path:
```
../save/MQ2007/1/clean/Perfect_training_seed1_state_1000.pkl
```
The structure includes the dataset name, fold ID, scenario type, click model, and training seed.

**File Naming Convention:**
```
{model}_training_seed{SEED}_state_{iterations}.pkl
```
The seed is included in the filename to support running multiple training runs with different seeds.


## Running Federated Unlearning Process

### Basic Usage
Run the unlearning script with the required method:
```bash
cd runs
python unlearn.py --unlearn_method retrain --train_seed 1 --unlearn_seed 100
```

### Complete Unlearning Example

To customize the unlearning process, you can pass arguments to the script. Below is an example of running the script with all available parameters:
```bash
cd runs
python unlearn.py \
  --dataset MQ2007 \
  --unlearn_method retrain \
  --train_seed 1 \
  --unlearn_seed 100 \
  --n_clients 10 \
  --interactions_per_feedback 5 \
  --interactions_budget 50000 \
  --learning_rate 0.1 \
  --update True \
  --n_malicious 3 \
  --scenario clean \
  --dataset_root_dir ../datasets \
  --save_dir ../save
```

### Important Parameters

- `--train_seed`: Seed of the pre-trained model to load (must match a previously trained model)
- `--unlearn_seed`: Seed for randomness during unlearning process
- `--unlearn_method`: Unlearning method to apply (retrain, FedRemove, fedEraser, fineTuning, pga)

**Backward Compatibility:** The old `--seed` parameter still works and will be used for both training and unlearning seeds if `--train_seed` and `--unlearn_seed` are not specified.

### Unlearning Outputs

After unlearning, results will also be saved in a `.pkl` file in the `save_dir`.

Example file path:
```
../save/MQ2007/1/clean/Perfect_training_seed1_unlearning_retrain_seed100_1000.pkl
```

**File Naming Convention:**
```
{model}_training_seed{TRAIN_SEED}_unlearning_{method}_seed{UNLEARN_SEED}_{iterations}.pkl
```
The filename includes both the training seed (which model was loaded) and the unlearning seed (randomness during unlearning).


## Evaluation

We provide comprehensive evaluation scripts that analyze results from both Algorithm 1 and Algorithm 2, showing mean performance and variance across seeds.

### Evaluation Scripts

#### For Algorithm 1 Results (Unlearning Variance)
```bash
cd Evaluation
python evaluate_algorithm1.py --dataset MQ2007 \
    --train_seed 1 \
    --unlearn_seed_start 100 \
    --unlearn_seed_end 109
```

**Outputs:**
- Plots showing mean NDCG@10 with ±1 std deviation across unlearning seeds
- Summary statistics (mean, std, min, max) for each unlearning method
- Files saved to `results/algorithm1/`

#### For Algorithm 2 Results (Pre-training Variance)
```bash
cd Evaluation
python evaluate_algorithm2.py --dataset MQ2007 \
    --seed_start 1 \
    --seed_end 10
```

**Outputs:**
- Plots showing mean NDCG@10 with ±1 std deviation across training seeds
- Summary statistics for both training and unlearning phases
- Variance comparison analysis between training and unlearning
- Files saved to `results/algorithm2/`

### Key Metrics

1. **Offline NDCG@10**: Ranking quality on test set at each epoch
2. **Online NDCG@10**: Cumulative performance during training/unlearning
3. **Standard Deviation**: Measures consistency across seeds (lower = more stable)
4. **RelR Difference**: Relevance Reset metric (requires `--enable_relr True`)

### Understanding Results

- **Narrow variance bands**: Method is stable and consistent
- **Wide variance bands**: Method is sensitive to random seed
- **Compare Algorithm 1 vs 2**: Identify whether unlearning or pre-training contributes more variance

For detailed evaluation instructions, see [Evaluation/README_EVALUATION.md](Evaluation/README_EVALUATION.md).

## Quick Start Guide

Here's a complete workflow from setup to evaluation:

### 1. Setup Environment
```bash
# Create environment
./setup_env.sh
conda activate foltr
pip install -r requirements.txt

# Fix line endings if needed
./dos2unix.sh
```

### 2. Prepare Datasets
```bash
# Download datasets (see Download datasets section above)
# Unpack to ./datasets/ folder
# Rename MSLR-WEB10K to MSLR10K
cd datasets
mv MSLR-WEB10K MSLR10K
cd ..
```

### 3. Run Experiments

**Option A: Test Unlearning Variance (Algorithm 1)**
```bash
./algorithm1.sh
# This trains 1 model and runs 10 unlearning experiments
# Takes several hours depending on hardware
```

**Option B: Test Pre-training Variance (Algorithm 2)**
```bash
./algorithm2.sh
# This trains 10 models and runs 10 unlearning experiments
# Takes longer than Algorithm 1
```

### 4. Evaluate Results
```bash
cd Evaluation

# For Algorithm 1 results
python evaluate_algorithm1.py --dataset MQ2007
python evaluate_algorithm1.py --dataset MSLR10K

# For Algorithm 2 results
python evaluate_algorithm2.py --dataset MQ2007
python evaluate_algorithm2.py --dataset MSLR10K
```

### 5. Check Results
- Plots: `Evaluation/results/algorithm1/` or `Evaluation/results/algorithm2/`
- Statistics: `*_summary.txt` and `*_variance_comparison.txt` files
- Interpretation guide: [Evaluation/README_EVALUATION.md](Evaluation/README_EVALUATION.md)

## Supplementary results

### Figures for Offline Performance (Mean nDCG@10)
- **MQ2007**
 
  No poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/MQ2007_Clean_offline.png)

  Data poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/MQ2007_Data_Poison_offline.png)

  Model poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/MQ2007_Model_Poison_offline.png)

  
- **MSLR-WEB10K**

  No poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/MSLR10K_Clean_offline.png)

  Data poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/MSLR10K_Data_Poison_offline.png)

  Model poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/MSLR10K_Model_Poison_offline.png)

  
- **Yahoo!**

  No poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/Yahoo_Clean_offline.png)

  Data poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/Yahoo_Data_Poison_offline.png)

  Model poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/Yahoo_Model_Poison_offline.png)

  
- **Istella-S**

  No poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/istella-s_Clean_offline.png)

  Data poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/istella-s_Data_Poison_offline.png)

  Model poisoning
  ![image](https://github.com/Iris1026/Unlearning-for-FOLTR/blob/main/Evaluation/results/istella-s_Model_Poison_offline.png)







