# 📊 Figures Guide: Boxplots Following Lanyon et al. (2025)

**Generated:** December 27, 2025  
**Style:** Following Lanyon et al. exactly - boxplots showing distributions

---

## 🎯 Main Figures for Your Paper

### Figure 1: Combined Multi-Panel Comparison ⭐
**File:** `figure_boxplot_combined.pdf` (or `.png`)

**What it shows:**
- Side-by-side boxplots for each method
- **Blue boxes:** Algorithm 1 (single training seed, common practice)
- **Red boxes:** Algorithm 2 (multiple training seeds, our recommendation)
- Three panels: Clean, Data Poisoning, Model Poisoning
- Gray reference lines show retrain quantiles (gold standard)

**Key insight visible:**
- FedRemove shows **narrow box** in Algorithm 1 (deterministic)
- FedRemove shows **wide box** in Algorithm 2 (training seed sensitive)
- Other methods show similar distributions across both algorithms

**Use this as your main comparison figure!**

---

### Figure 2: FedRemove Focused ⭐
**File:** `figure_fedremove_comparison.pdf` (or `.png`)

**What it shows:**
- Only FedRemove, comparing Algorithm 1 vs Algorithm 2 directly
- Shows **outliers** (black diamonds) for failures
- Green dashed line = retrain gold standard

**Key insight visible:**
- **Clean:** Algorithm 1 appears narrow (deterministic), Algorithm 2 wider
- **Data Poisoning:** Both algorithms show FedRemove stays at ~0.2 (failure visible!)
- **Model Poisoning:** Huge variance in Algorithm 2, some outliers very low

**Perfect for highlighting the problem!**

---

## 📁 Individual Scenario Figures

### Clean Scenario
**File:** `figure_boxplot_clean.pdf/png`
- Shows all methods perform similarly
- Minimal difference between Algorithm 1 and 2
- FedRemove deterministic behavior visible (no variance in Algo 1)

### Data Poisoning
**File:** `figure_boxplot_data_poison.pdf/png`
- **Dramatic:** FedRemove boxes are much lower than others (~0.2 vs ~0.53)
- Shows FedRemove failure to recover from poisoning
- Other methods recover well

### Model Poisoning  
**File:** `figure_boxplot_model_poison.pdf/png`
- FedRemove shows **large spread** in Algorithm 2
- Some training seeds lead to complete failure
- Other methods remain robust

---

## 📊 How to Interpret Boxplots

### Box Elements:
- **Box:** Interquartile range (IQR) = 25th to 75th percentile
- **Line in box:** Median (50th percentile)
- **Whiskers:** Extend to 1.5× IQR from quartiles
- **Diamonds:** Outliers beyond whiskers

### What to Look For:
1. **Narrow box = Low variance** (consistent across seeds)
2. **Wide box = High variance** (sensitive to seed choice)
3. **Different medians = Distributional shift** between algorithms
4. **Outliers = Catastrophic failures** for specific seeds

---

## 🎓 For Your Paper

### LaTeX Include

```latex
\begin{figure}[ht]
    \centering
    \includegraphics[width=0.95\textwidth]{figure_boxplot_combined.pdf}
    \caption{Evaluation protocol sensitivity comparison. Boxplots show 
    performance distributions under Algorithm 1 (single training seed, blue) 
    and Algorithm 2 (multiple training seeds, red). FedRemove exhibits 
    deterministic behavior in Algorithm 1 (narrow box) but high variance in 
    Algorithm 2 (wide box), particularly under adversarial scenarios, 
    demonstrating that single-seed evaluation masks method instability.}
    \label{fig:boxplot_comparison}
\end{figure}
```

### Alternative: FedRemove Focused

```latex
\begin{figure}[ht]
    \centering
    \includegraphics[width=0.95\textwidth]{figure_fedremove_comparison.pdf}
    \caption{FedRemove performance under single-seed (Algorithm 1) vs 
    multi-seed (Algorithm 2) evaluation. In clean scenarios, both protocols 
    appear similar. Under data and model poisoning, Algorithm 2 reveals high 
    variance and catastrophic failures (outliers) that are completely hidden 
    by Algorithm 1's deterministic evaluation. Green dashed line indicates 
    retrain gold standard.}
    \label{fig:fedremove_focus}
\end{figure}
```

---

## 📝 Key Claims Supported by Figures

### From Combined Boxplot (Figure 1):

**Claim 1:**
> "Figure~\ref{fig:boxplot_comparison} shows performance distributions for each 
> method under both evaluation protocols. In clean scenarios, all methods exhibit 
> similar distributions regardless of protocol. However, under adversarial attacks, 
> FedRemove shows narrow distribution in Algorithm 1 (deterministic) but wide 
> distribution in Algorithm 2, revealing training seed sensitivity."

**Claim 2:**
> "The median FedRemove performance under data poisoning is NDCG@10 ≈ 0.20 
> regardless of protocol, but Algorithm 2 reveals variance (IQR = 0.18-0.24) 
> that is completely absent in Algorithm 1 (IQR ≈ 0), demonstrating that 
> deterministic methods appear deceptively stable under single-seed evaluation."

### From FedRemove Focused (Figure 2):

**Claim 3:**
> "Figure~\ref{fig:fedremove_focus} isolates FedRemove to highlight the 
> evaluation protocol problem. While Algorithm 1 suggests consistent behavior 
> (narrow boxplots), Algorithm 2 exposes substantial variance and outliers 
> representing catastrophic failures for specific training seeds, particularly 
> under model poisoning where some seeds achieve NDCG@10 < 0.20 while others 
> reach 0.40+."

---

## 🔄 Comparison to Other Visualizations

### You Now Have Three Types of Figures:

1. **Boxplots** (These files) 
   - Show **distributions** directly
   - Following Lanyon et al. style
   - **Best for:** Comparing evaluation protocols

2. **W2 Bar Charts** (`CORRECT_ALGO1_VS_ALGO2_W2.png`)
   - Show **distributional distance** (summary metric)
   - Quantifies protocol sensitivity
   - **Best for:** Ranking methods by robustness

3. **Performance Trajectories** (`algorithm*/MQ2007_*.png`)
   - Show **temporal evolution** during training/unlearning
   - Reveal when failures occur
   - **Best for:** Understanding unlearning dynamics

**Use all three types for a complete picture!**

---

## ✅ What Makes These Correct

Following Lanyon et al. (2025) exactly:

1. ✅ **Boxplots** not tables - show actual distributions
2. ✅ **Side-by-side** comparison of Algorithm 1 vs Algorithm 2
3. ✅ **Reference lines** for gold standard (retrain)
4. ✅ **Shows variance** through box width
5. ✅ **Outliers visible** as individual points
6. ✅ **Multi-panel** for different scenarios

---

## 📂 Files Summary

```
results/
│
├── 📊 MAIN FIGURES (Use these!):
│   ├── figure_boxplot_combined.pdf/png           ← Main comparison ⭐
│   ├── figure_fedremove_comparison.pdf/png       ← FedRemove focus ⭐
│   
├── 📊 INDIVIDUAL SCENARIOS:
│   ├── figure_boxplot_clean.pdf/png
│   ├── figure_boxplot_data_poison.pdf/png
│   └── figure_boxplot_model_poison.pdf/png
│   
├── 📊 SUPPLEMENTARY:
│   ├── CORRECT_ALGO1_VS_ALGO2_W2.png            ← W2 distances
│   └── algorithm2/MQ2007_*.png                   ← Trajectories
│
└── 📄 (Old LaTeX tables - can be removed or kept as supplementary)
    ├── table1_w2_distances.tex
    ├── table2_fedremove_detail.tex
    └── table3_method_rankings.tex
```

---

## 🚀 Regenerating (If Needed)

```bash
cd Evaluation

# Ensure data is exported
python export_results_to_csv.py

# Generate boxplot figures
python create_boxplot_figures.py
```

---

**✅ Now following Lanyon et al. (2025) visualization style exactly!**

**Boxplots show the actual distributions, not just summary statistics.**  
**Outliers and failures are visible, not hidden!**

