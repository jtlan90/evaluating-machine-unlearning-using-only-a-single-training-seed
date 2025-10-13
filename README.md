# Methadological Considerations for Machine Unlearning

## Based on the SSD codebase
https://github.com/if-loops/selective-synaptic-dampening
This directory contains an implementation of various machine unlearning strategies for deep neural networks, including:

- **Selective Synaptic Dampening (SSD)**
- **Loss Free Selective Synaptic Dampening (LFSSD)**
- **Fisher Forgetting**
- **Amnesiac Unlearning** 
- **UNSIR**
- **Random Labels**
- **NTK**
- **Retrain** (baseline)



## Setting up environments

Install required packages and setup conda env:
```bash
cd src
./setup_env.sh
conda activate forget
pip install -r requirements.txt
``` 

## Running Experiments

Bash scripts are provided for running experiments:
- `algorithm1.sh`: Run Algorith 1: A in the paper
- `algorithm2.sh`: Run Algorith 2: B in the paper