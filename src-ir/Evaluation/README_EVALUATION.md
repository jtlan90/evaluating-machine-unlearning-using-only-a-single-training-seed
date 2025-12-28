# Evaluation Guide for Machine Unlearning Experiments

This guide explains how to analyze results from Algorithm 1 and Algorithm 2.

## Overview

### Algorithm 1: Testing Unlearning Variance
- **Fixed**: 1 pre-trained model (seed 1)
- **Varies**: 10 unlearning runs (seeds 100-109)
- **Purpose**: Measure variance introduced by unlearning randomness

### Algorithm 2: Testing Pre-training Variance
- **Fixed**: Matching train/unlearn seeds (e.g., both use seed 1)
- **Varies**: 10 different pre-trained models (seeds 1-10)
- **Purpose**: Measure variance introduced by pre-training randomness

---

## Running Evaluations

### For Algorithm 1 Results

```bash
cd Evaluation

# Evaluate MQ2007 results
python evaluate_algorithm1.py --dataset MQ2007 \
    --train_seed 1 \
    --unlearn_seed_start 100 \
    --unlearn_seed_end 109 \
    --base_dir ../save \
    --save_dir results/algorithm1

# Evaluate MSLR10K results
python evaluate_algorithm1.py --dataset MSLR10K \
    --train_seed 1 \
    --unlearn_seed_start 100 \
    --unlearn_seed_end 109 \
    --base_dir ../save \
    --save_dir results/algorithm1
```

**Outputs:**
- `results/algorithm1/{dataset}_{scenario}_algorithm1.png` - Plots showing mean ± std deviation
- `results/algorithm1/{dataset}_algorithm1_summary.txt` - Statistical summary tables

### For Algorithm 2 Results

```bash
cd Evaluation

# Evaluate MQ2007 results
python evaluate_algorithm2.py --dataset MQ2007 \
    --seed_start 1 \
    --seed_end 10 \
    --base_dir ../save \
    --save_dir results/algorithm2

# Evaluate MSLR10K results
python evaluate_algorithm2.py --dataset MSLR10K \
    --seed_start 1 \
    --seed_end 10 \
    --base_dir ../save \
    --save_dir results/algorithm2
```

**Outputs:**
- `results/algorithm2/{dataset}_{scenario}_algorithm2.png` - Plots showing mean ± std deviation
- `results/algorithm2/{dataset}_algorithm2_summary.txt` - Statistical summary tables
- `results/algorithm2/{dataset}_variance_comparison.txt` - Variance analysis

---

## Understanding the Plots

### Plot Elements

1. **Training Phase (Epochs 0-1000)**:
   - Blue line shows training NDCG@10
   - Shaded area shows ±1 std deviation across runs
   - For Algorithm 1: Single run (no variance)
   - For Algorithm 2: Mean across 10 runs (shows training variance)

2. **Unlearning Phase (Epochs 1000-2000)**:
   - Colored lines show different unlearning methods
   - Shaded areas show ±1 std deviation
   - Narrower bands = more stable method
   - Wider bands = more sensitive to random seed

3. **Vertical Dashed Line**: Separates training from unlearning phases

### Interpreting Results

**Algorithm 1 Analysis:**
- If unlearning methods show **small variance** → Method is stable regardless of random initialization
- If unlearning methods show **large variance** → Method is sensitive to random seed

**Algorithm 2 Analysis:**
- If training shows **small variance** → Pre-training is stable
- If training shows **large variance** → Pre-training randomness matters
- Compare unlearning variance to training variance to see which dominates

---

## Summary Statistics

Both evaluation scripts generate text summaries with:

### Mean and Standard Deviation
```
Method          Mean       Std        Min        Max
retrain         0.4523     0.0012     0.4501     0.4545
FedRemove       0.4489     0.0008     0.4476     0.4502
fedEraser       0.4512     0.0015     0.4490     0.4538
fineTuning      0.4501     0.0010     0.4485     0.4520
pga             0.4490     0.0020     0.4455     0.4525
```

**Interpretation:**
- **Mean**: Average performance across all seeds
- **Std**: How much variation exists (lower = more consistent)
- **Min/Max**: Range of performance

---

## Key Metrics Explained

### 1. Offline NDCG@10
- Measures ranking quality on test set
- Higher is better (0 to 1)
- Evaluated at each epoch

### 2. Online NDCG@10  
- Cumulative performance during training/unlearning
- Accounts for user interactions over time
- Discount factor makes recent epochs more important

### 3. Standard Deviation
- Measures consistency across seeds
- Lower std = more reliable/stable method
- Compare stds between Algorithm 1 and 2 to identify variance source

---

## Comparing Algorithms

### Key Questions to Answer:

1. **Which source of variance is larger?**
   - Algorithm 1 (unlearning) vs Algorithm 2 (pre-training)
   - Check std values in summary files

2. **Which unlearning methods are most stable?**
   - Look for smallest std in Algorithm 1 results
   - Stable methods are preferable in production

3. **Does pre-training quality affect unlearning?**
   - Check correlation between training final NDCG and unlearning final NDCG in Algorithm 2
   - High correlation = pre-training matters more

4. **Best case vs Worst case?**
   - Check Min/Max values
   - Large gaps indicate high sensitivity

---

## Troubleshooting

### Missing Files

If evaluation fails with "file not found":

1. **Check file naming**: Ensure training/unlearning completed successfully
2. **Verify paths**: Files should be in `save/{dataset}/{fold}/{scenario}/`
3. **Check seed ranges**: Make sure they match what you ran in algorithms

### Expected File Structure

```
save/
├── MQ2007/
│   └── 1/
│       ├── clean/
│       │   ├── Perfect_training_seed1_state_1000.pkl
│       │   ├── Perfect_training_seed1_unlearning_retrain_seed100_1000.pkl
│       │   ├── Perfect_training_seed1_unlearning_retrain_seed101_1000.pkl
│       │   └── ...
│       ├── data/
│       └── model/
└── MSLR10K/
    └── ...
```

### No Plots Generated

- Check that `matplotlib` and `seaborn` are installed
- Ensure `save_dir` is writable
- Look for error messages in console output

---

## Advanced Usage

### Custom Seed Ranges

If you ran experiments with different seed ranges:

```bash
# Algorithm 1 with custom seeds
python evaluate_algorithm1.py \
    --dataset MQ2007 \
    --train_seed 42 \
    --unlearn_seed_start 1000 \
    --unlearn_seed_end 1019

# Algorithm 2 with custom seeds
python evaluate_algorithm2.py \
    --dataset MQ2007 \
    --seed_start 50 \
    --seed_end 59
```

### Specific Scenarios Only

Edit the `scenarios` list in the scripts:

```python
# In evaluate_algorithm1.py or evaluate_algorithm2.py
scenarios = ['clean']  # Only evaluate clean scenario
# scenarios = ['data_poison', 'model_poison']  # Only poisoning scenarios
```

---

## Quick Reference

| Task | Command |
|------|---------|
| Evaluate Algorithm 1 | `python evaluate_algorithm1.py --dataset MQ2007` |
| Evaluate Algorithm 2 | `python evaluate_algorithm2.py --dataset MQ2007` |
| Change seed range | Add `--unlearn_seed_start X --unlearn_seed_end Y` |
| Custom output dir | Add `--save_dir my_results/` |
| Different dataset | Change `--dataset` to MSLR10K, Yahoo, or istella-s |

---

## Citation

If you use these evaluation scripts, please cite the original paper:

```
[Paper citation to be added]
```

