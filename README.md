# On the limitation of evaluating machine unlearning using only a single training seed

This repository examines the impact of using multiple baseline models for machine unlearning evaluation across two domains: **Computer Vision** and **Information Retrieval**.

## Repository Structure

- **`src-vis/`**: Computer Vision experiments (based on the SSD codebase: https://github.com/if-loops/selective-synaptic-dampening)
- **`src-ir/`**: Information Retrieval experiments (federated learning to rank) based on the codebase: https://github.com/Iris1026/Unlearning-for-FOLTR

---

## Computer Vision Experiments (`src-vis`)

### Unlearning Methods Implemented

The following machine unlearning methods for deep neural networks are available:

- **Selective Synaptic Dampening (SSD)**
- **Loss Free Selective Synaptic Dampening (LFSSD)**
- **Fisher Forgetting**
- **Amnesiac Unlearning** 
- **UNSIR**
- **Random Labels**
- **NTK**
- **Retrain** (baseline)

### Setting up Environment

Install required packages and setup conda env:
```bash
cd src-vis
./setup_env.sh
conda activate forget
pip install -r requirements.txt
``` 

### Running Experiments

Bash scripts are provided for running experiments:
- `algorithm1.sh`: Run Algorithm 1 from the paper
- `algorithm2.sh`: Run Algorithm 2 from the paper

---

## Information Retrieval Experiments (`src-ir`)

### Unlearning Methods Implemented

The following federated unlearning methods for learning-to-rank models are available:

- **Retrain** (baseline)
- **FedRemove**
- **FedEraser**
- **Fine Tuning**
- **PGA (Gradient Ascent)**

### Scenarios Tested

- **Clean**: No poisoning
- **Data Poison**: Malicious data injection
- **Model Poison**: Malicious model updates

### Setting up Environment

Install required packages and setup conda env:
```bash
cd src-ir
./setup_env.sh
conda activate foltr
pip install -r requirements.txt
```

### Running Experiments

Bash scripts are provided for running experiments:
- `algorithm1.sh`: Run Algorithm 1 (training only)
- `algorithm2.sh`: Run Algorithm 2 (training + unlearning)
