# Analysis Results: Lanyon et al. Replication in FOLTR

**Dataset:** MQ2007  
**Experiments:** 4,624 total (Algorithm 1: 2,312, Algorithm 2: 2,312)  
**Methodology:** Following Lanyon et al. (2025) exactly  

---

## 📊 FOR YOUR PAPER: Use These Files

### Main Figure
- **`CORRECT_ALGO1_VS_ALGO2_W2.png`** ← Primary figure showing W2 distances between evaluation protocols
  - ONE bar per method (correct methodology)
  - Shows FedRemove W2 = 0.068 in model poisoning (23× higher than retrain)

### LaTeX Tables (Ready to Use)
1. **`table1_w2_distances.tex`** - W2 distances by scenario
2. **`table2_fedremove_detail.tex`** - FedRemove detailed comparison
3. **`table3_method_rankings.tex`** - Method rankings by robustness

### Numerical Data
- **`CORRECT_ALGO1_VS_ALGO2_W2.txt`** - All W2 distances and statistics

---

## 📄 Documentation

### Quick Start
- **`PAPER_FILES_GUIDE.md`** ← Read this first for paper writing

### Comprehensive Summaries
- **`FINAL_EXECUTIVE_SUMMARY_CORRECTED.md`** - Full analysis with LaTeX templates
- **`CORRECTED_W2_ANALYSIS_SUMMARY.md`** - Detailed W2 methodology explanation
- **`LANYON_REPLICATION_FINDINGS.md`** - Key findings summary

### Reference
- **`W2_CORRECTION_SUMMARY.md`** - What was corrected from initial analysis
- **`COMPREHENSIVE_ALGORITHM_COMPARISON.md`** - Detailed 10-seed comparison

---

## 📁 Directory Structure

```
results/
│
├── README.md                                   ← This file
│
├── ✅ FOR PAPER:
│   ├── CORRECT_ALGO1_VS_ALGO2_W2.png          ← Main figure
│   ├── CORRECT_ALGO1_VS_ALGO2_W2.txt          ← Numerical data
│   ├── table1_w2_distances.tex                ← LaTeX table 1
│   ├── table2_fedremove_detail.tex            ← LaTeX table 2
│   └── table3_method_rankings.tex             ← LaTeX table 3
│
├── 📄 DOCUMENTATION:
│   ├── PAPER_FILES_GUIDE.md                   ← Quick reference
│   ├── FINAL_EXECUTIVE_SUMMARY_CORRECTED.md   ← Full summary
│   ├── CORRECTED_W2_ANALYSIS_SUMMARY.md       ← Detailed explanation
│   ├── W2_CORRECTION_SUMMARY.md               ← What was corrected
│   ├── LANYON_REPLICATION_FINDINGS.md         ← Findings summary
│   └── COMPREHENSIVE_ALGORITHM_COMPARISON.md  ← Detailed analysis
│
├── 📊 SUPPORTING FIGURES:
│   ├── algorithm1/
│   │   ├── MQ2007_clean_algorithm1.png
│   │   ├── MQ2007_data_poison_algorithm1.png
│   │   ├── MQ2007_model_poison_algorithm1.png
│   │   ├── MQ2007_*_w2_trajectory.png
│   │   ├── MQ2007_algorithm1_summary.txt
│   │   └── MQ2007_algorithm1_w2_distances.txt
│   │
│   └── algorithm2/
│       ├── MQ2007_clean_algorithm2.png
│       ├── MQ2007_data_poison_algorithm2.png
│       ├── MQ2007_model_poison_algorithm2.png
│       ├── MQ2007_*_w2_trajectory.png
│       ├── MQ2007_algorithm2_summary.txt
│       ├── MQ2007_algorithm2_w2_distances.txt
│       └── MQ2007_pairwise_w2_pretrain_sensitivity.txt
│
└── data/
    └── MQ2007_all_results.csv                 ← Raw data export
```

---

## 🎯 Key Findings

### Main Result
**FedRemove shows W2 = 0.068 between single-seed and multi-seed evaluation protocols in adversarial scenarios, 23× higher than retrain (W2 = 0.003).**

### By Scenario

| Scenario | FedRemove W2 | Retrain W2 | Ratio | Interpretation |
|----------|--------------|------------|-------|----------------|
| Clean | 0.0034 | 0.0030 | 1.1× | Negligible |
| Data Poisoning | 0.0199 | 0.0036 | 5.6× | Moderate sensitivity |
| Model Poisoning | **0.0677** | 0.0030 | **22.9×** | High sensitivity 🚨 |

### Practical Impact
For Informational model under model poisoning:
- **Single-seed evaluation:** NDCG = 0.342 ± 0.000 (appears stable)
- **Multi-seed evaluation:** NDCG = 0.269 ± 0.061 (reveals instability)
- **Overestimate:** 27%
- **W2 distance:** 0.096 (quantifies distributional difference)

---

## 📝 How to Use in LaTeX

### Preamble
```latex
\usepackage{booktabs}
\usepackage{graphicx}
```

### Include Figure
```latex
\begin{figure}[ht]
    \centering
    \includegraphics[width=0.9\textwidth]{CORRECT_ALGO1_VS_ALGO2_W2.png}
    \caption{Wasserstein-2 distances between Algorithm 1 (single training seed) 
    and Algorithm 2 (multiple training seeds) performance distributions.}
    \label{fig:w2_comparison}
\end{figure}
```

### Include Tables
```latex
\input{table1_w2_distances.tex}
\input{table2_fedremove_detail.tex}
\input{table3_method_rankings.tex}
```

---

## 🔄 Regenerating Results (If Needed)

### Step 1: Export Data to CSV
```bash
cd Evaluation
python export_results_to_csv.py
```

### Step 2: Generate LaTeX Tables
```bash
python generate_latex_tables.py
```

### Step 3: Generate Figures (if R is available)
```bash
Rscript create_figures_ir.R
```

Or use Python alternative:
```bash
python compare_algo1_vs_algo2_correct.py
```

---

## ✅ What Was Cleaned Up

### Deleted Files (Incorrect Methodology)
- ❌ `ALGO1_VS_ALGO2_W2_COMPARISON.png` - TWO bars per method (wrong!)
- ❌ `FEDREMOVE_TRAINING_SENSITIVITY.png` - From old analysis
- ❌ Old offline plots (istella-s, MSLR10K, Yahoo)
- ❌ 9 redundant/outdated markdown files

### Why They Were Wrong
The deleted comparison showed variance **within** each algorithm instead of difference **between** algorithms. Lanyon et al.'s methodology computes W2 distance **between** Algorithm 1 and Algorithm 2 distributions:

```r
# Lanyon et al. line 369:
distance = wasserstein1d(algorithm_1_results, algorithm_2_results, p = 2)
```

---

## 🎓 Citation

If using these results, cite both the replication and original:

```bibtex
@article{lanyon2025limitation,
  title={On the limitation of evaluating machine unlearning using only a single training seed},
  author={Lanyon, Jamie and ...},
  year={2025}
}
```

---

## 📞 Questions?

**Need quick guidance?** → `PAPER_FILES_GUIDE.md`  
**Need full context?** → `FINAL_EXECUTIVE_SUMMARY_CORRECTED.md`  
**Need detailed explanation?** → `CORRECTED_W2_ANALYSIS_SUMMARY.md`

---

**Last Updated:** December 27, 2025  
**Status:** ✅ Publication-ready following Lanyon et al. (2025) methodology exactly

