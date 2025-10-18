# On the limitation of evaluating machine unlearning using only a single training seed

## Based on the SSD codebase
https://github.com/if-loops/selective-synaptic-dampening


Examines the impact of using multiple baseline models for machine unlearning evaluation with implementations for the following machine unlearning methods for deep neural networks, including:

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
- `algorithm1.sh`: Run Algorithm 1: A in the paper
- `algorithm2.sh`: Run Algorithm 2: B in the paper
