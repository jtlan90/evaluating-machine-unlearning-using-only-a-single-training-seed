#!/usr/bin/env Rscript
# Analysis of federated unlearning in information retrieval
# Following Lanyon et al. (2025) methodology

library(tidyverse)
library(transport)  # provides wasserstein1d(x, y, p = 2)
library(xtable)     # for LaTeX table generation

# Configuration
fig_width <- 7
fig_height <- 5
output_dir <- "results"
data_file <- "results/data/MQ2007_all_results.csv"

# Load data
cat("Loading data from", data_file, "\n")
data_tbl <- read_csv(data_file, show_col_types = FALSE)

# Factor levels for consistent ordering
scenario_levels <- c("clean", "data_poison", "model_poison")
scenario_labels <- c("Clean", "Data Poisoning", "Model Poisoning")

model_levels <- c("Perfect", "Navigational", "Informational")
method_levels <- c("retrain", "FedRemove", "fedEraser", "fineTuning", "pga")
method_labels <- c("Retrain", "FedRemove", "FedEraser", "FineTuning", "PGA")

# Apply factor levels
data_tbl <- data_tbl %>%
  mutate(
    scenario = factor(scenario, levels = scenario_levels),
    model = factor(model, levels = model_levels),
    method = factor(method, levels = method_levels),
    algorithm = factor(algorithm, levels = c(1, 2))
  )

cat("Data loaded:", nrow(data_tbl), "observations\n")
cat("Algorithms:", unique(data_tbl$algorithm), "\n")
cat("Scenarios:", levels(data_tbl$scenario), "\n")
cat("Methods:", levels(data_tbl$method), "\n\n")

# --------------------------------------------------------------------------- #
# Compute Wasserstein-2 distances between Algorithm 1 and Algorithm 2
# Following Lanyon et al. line 369: 
#   distance = wasserstein1d(algorithm_1_results, algorithm_2_results, p = 2)
# --------------------------------------------------------------------------- #

cat("Computing Wasserstein-2 distances...\n")

w2_tbl <- tibble()

for (s in scenario_levels) {
  for (m in model_levels) {
    for (meth in method_levels) {
      
      # Get Algorithm 1 distribution (fixed training seed, varying unlearning seeds)
      algo1_results <- data_tbl %>%
        filter(algorithm == 1, scenario == s, model == m, method == meth) %>%
        pull(ndcg)
      
      # Get Algorithm 2 distribution (varying training seeds, matching unlearning seeds)
      algo2_results <- data_tbl %>%
        filter(algorithm == 2, scenario == s, model == m, method == meth) %>%
        pull(ndcg)
      
      if (length(algo1_results) > 0 && length(algo2_results) > 0) {
        w2_dist <- wasserstein1d(algo1_results, algo2_results, p = 2)
        
        w2_tbl <- w2_tbl %>%
          bind_rows(tibble(
            scenario = s,
            model = m,
            method = meth,
            w2_distance = w2_dist,
            algo1_mean = mean(algo1_results),
            algo1_sd = sd(algo1_results),
            algo2_mean = mean(algo2_results),
            algo2_sd = sd(algo2_results)
          ))
      }
    }
  }
}

cat("Computed", nrow(w2_tbl), "W2 distances\n\n")

# --------------------------------------------------------------------------- #
# Generate LaTeX Table 1: W2 distances by scenario
# --------------------------------------------------------------------------- #

cat("Generating LaTeX Table 1: W2 distances by scenario...\n")

# Average across models for each method and scenario
w2_summary <- w2_tbl %>%
  group_by(scenario, method) %>%
  summarise(
    w2_mean = mean(w2_distance),
    .groups = "drop"
  ) %>%
  pivot_wider(names_from = scenario, values_from = w2_mean) %>%
  arrange(match(method, method_levels))

# Format for LaTeX
w2_summary_latex <- w2_summary %>%
  mutate(
    method = recode(method, !!!setNames(method_labels, method_levels)),
    clean = sprintf("%.4f", clean),
    data_poison = sprintf("%.4f", data_poison),
    model_poison = sprintf("%.4f", model_poison)
  ) %>%
  rename(
    Method = method,
    Clean = clean,
    `Data Poisoning` = data_poison,
    `Model Poisoning` = model_poison
  )

# Generate LaTeX
latex_table1 <- xtable(
  w2_summary_latex,
  caption = "Wasserstein-2 distances between Algorithm 1 (single training seed) and Algorithm 2 (multiple training seeds) performance distributions. Higher values indicate greater sensitivity to evaluation protocol choice.",
  label = "tab:w2_distances",
  align = c("l", "l", "r", "r", "r")
)

print(latex_table1, 
      file = file.path(output_dir, "table1_w2_distances.tex"),
      include.rownames = FALSE,
      caption.placement = "top",
      booktabs = TRUE,
      sanitize.text.function = identity)

cat("✅ Saved: results/table1_w2_distances.tex\n\n")

# --------------------------------------------------------------------------- #
# Generate LaTeX Table 2: Detailed FedRemove comparison
# --------------------------------------------------------------------------- #

cat("Generating LaTeX Table 2: FedRemove detailed comparison...\n")

fedremove_detail <- w2_tbl %>%
  filter(method == "FedRemove") %>%
  select(scenario, model, w2_distance, algo1_mean, algo1_sd, algo2_mean, algo2_sd) %>%
  mutate(
    scenario = recode(scenario, !!!setNames(scenario_labels, scenario_levels)),
    algo1_formatted = sprintf("%.3f $\\pm$ %.3f", algo1_mean, algo1_sd),
    algo2_formatted = sprintf("%.3f $\\pm$ %.3f", algo2_mean, algo2_sd),
    w2_formatted = sprintf("%.4f", w2_distance)
  ) %>%
  select(scenario, model, algo1_formatted, algo2_formatted, w2_formatted) %>%
  rename(
    Scenario = scenario,
    Model = model,
    `Algorithm 1` = algo1_formatted,
    `Algorithm 2` = algo2_formatted,
    `W2 Distance` = w2_formatted
  )

latex_table2 <- xtable(
  fedremove_detail,
  caption = "FedRemove performance under single-seed (Algorithm 1) and multi-seed (Algorithm 2) evaluation protocols. Algorithm 1 shows zero standard deviation (deterministic), while Algorithm 2 reveals high variance (training seed sensitivity).",
  label = "tab:fedremove_detail",
  align = c("l", "l", "l", "r", "r", "r")
)

print(latex_table2,
      file = file.path(output_dir, "table2_fedremove_detail.tex"),
      include.rownames = FALSE,
      caption.placement = "top",
      booktabs = TRUE,
      sanitize.text.function = identity)

cat("✅ Saved: results/table2_fedremove_detail.tex\n\n")

# --------------------------------------------------------------------------- #
# Generate LaTeX Table 3: Method rankings by scenario
# --------------------------------------------------------------------------- #

cat("Generating LaTeX Table 3: Method rankings...\n")

method_rankings <- w2_tbl %>%
  group_by(scenario, method) %>%
  summarise(w2_mean = mean(w2_distance), .groups = "drop") %>%
  group_by(scenario) %>%
  arrange(w2_mean) %>%
  mutate(rank = row_number()) %>%
  ungroup() %>%
  select(scenario, rank, method, w2_mean) %>%
  mutate(
    scenario = recode(scenario, !!!setNames(scenario_labels, scenario_levels)),
    method = recode(method, !!!setNames(method_labels, method_levels)),
    w2_formatted = sprintf("%.4f", w2_mean),
    interpretation = case_when(
      w2_mean < 0.01 ~ "Robust",
      w2_mean < 0.05 ~ "Moderate",
      TRUE ~ "High sensitivity"
    )
  ) %>%
  select(scenario, rank, method, w2_formatted, interpretation) %>%
  rename(
    Scenario = scenario,
    Rank = rank,
    Method = method,
    `W2 Distance` = w2_formatted,
    Interpretation = interpretation
  )

latex_table3 <- xtable(
  method_rankings,
  caption = "Method rankings by evaluation protocol robustness. Methods are ranked by mean W2 distance (lower is better) within each scenario.",
  label = "tab:method_rankings",
  align = c("l", "l", "c", "l", "r", "l")
)

print(latex_table3,
      file = file.path(output_dir, "table3_method_rankings.tex"),
      include.rownames = FALSE,
      caption.placement = "top",
      booktabs = TRUE,
      sanitize.text.function = identity)

cat("✅ Saved: results/table3_method_rankings.tex\n\n")

# --------------------------------------------------------------------------- #
# Generate Figure 1: W2 distances by scenario (bar plot)
# --------------------------------------------------------------------------- #

cat("Generating Figure 1: W2 distances comparison...\n")

# Compute average W2 across models
w2_plot_data <- w2_tbl %>%
  group_by(scenario, method) %>%
  summarise(w2_mean = mean(w2_distance), .groups = "drop") %>%
  mutate(
    scenario = factor(scenario, levels = scenario_levels, labels = scenario_labels),
    method = factor(method, levels = method_levels, labels = method_labels)
  )

# Color palette
colors <- c(
  "Retrain" = "#3498db",
  "FedRemove" = "#e74c3c",
  "FedEraser" = "#2ecc71",
  "FineTuning" = "#f39c12",
  "PGA" = "#9b59b6"
)

fig1 <- ggplot(w2_plot_data, aes(x = method, y = w2_mean, fill = method)) +
  geom_bar(stat = "identity", alpha = 0.8, color = "black", linewidth = 0.5) +
  geom_text(aes(label = sprintf("%.4f", w2_mean)), 
            vjust = -0.5, size = 3, fontface = "bold") +
  geom_hline(yintercept = 0.01, linetype = "dashed", color = "darkgreen", alpha = 0.5) +
  geom_hline(yintercept = 0.05, linetype = "dashed", color = "darkorange", alpha = 0.5) +
  geom_hline(yintercept = 0.1, linetype = "dashed", color = "darkred", alpha = 0.5) +
  facet_wrap(~ scenario, ncol = 3) +
  scale_fill_manual(values = colors) +
  labs(
    title = "Wasserstein-2 Distance Between Algorithm 1 and Algorithm 2",
    subtitle = "Higher W2 = Evaluation protocol choice affects method performance",
    x = "Method",
    y = expression(paste(W[2], " Distance (Algo1 vs Algo2)")),
    fill = "Method"
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold", hjust = 0.5),
    plot.subtitle = element_text(size = 11, hjust = 0.5),
    axis.text.x = element_text(angle = 45, hjust = 1),
    legend.position = "none",
    strip.text = element_text(size = 12, face = "bold"),
    panel.grid.major.x = element_blank()
  )

ggsave(
  file.path(output_dir, "figure1_w2_comparison.pdf"),
  fig1,
  width = fig_width * 1.5,
  height = fig_height,
  device = "pdf"
)

ggsave(
  file.path(output_dir, "figure1_w2_comparison.png"),
  fig1,
  width = fig_width * 1.5,
  height = fig_height,
  dpi = 300
)

cat("✅ Saved: results/figure1_w2_comparison.pdf\n")
cat("✅ Saved: results/figure1_w2_comparison.png\n\n")

# --------------------------------------------------------------------------- #
# Generate Figure 2: FedRemove escalation across scenarios
# --------------------------------------------------------------------------- #

cat("Generating Figure 2: FedRemove escalation...\n")

fedremove_escalation <- w2_tbl %>%
  filter(method == "FedRemove") %>%
  group_by(scenario) %>%
  summarise(w2_mean = mean(w2_distance), .groups = "drop") %>%
  mutate(scenario = factor(scenario, levels = scenario_levels, labels = scenario_labels))

fig2 <- ggplot(fedremove_escalation, aes(x = scenario, y = w2_mean)) +
  geom_bar(stat = "identity", fill = "#e74c3c", alpha = 0.8, color = "black", linewidth = 1) +
  geom_text(aes(label = sprintf("%.4f", w2_mean)), 
            vjust = -0.5, size = 5, fontface = "bold") +
  geom_hline(yintercept = 0.01, linetype = "dashed", color = "darkgreen", 
             alpha = 0.5, linewidth = 1) +
  geom_hline(yintercept = 0.05, linetype = "dashed", color = "darkorange", 
             alpha = 0.5, linewidth = 1) +
  labs(
    title = "FedRemove: Evaluation Protocol Sensitivity Escalation",
    subtitle = "Adversarial attacks amplify sensitivity to evaluation protocol choice",
    x = "Scenario",
    y = expression(paste(W[2], " Distance (Algo1 vs Algo2)"))
  ) +
  theme_minimal() +
  theme(
    plot.title = element_text(size = 14, face = "bold", hjust = 0.5),
    plot.subtitle = element_text(size = 11, hjust = 0.5),
    axis.text.x = element_text(size = 12),
    panel.grid.major.x = element_blank()
  )

ggsave(
  file.path(output_dir, "figure2_fedremove_escalation.pdf"),
  fig2,
  width = fig_width,
  height = fig_height,
  device = "pdf"
)

ggsave(
  file.path(output_dir, "figure2_fedremove_escalation.png"),
  fig2,
  width = fig_width,
  height = fig_height,
  dpi = 300
)

cat("✅ Saved: results/figure2_fedremove_escalation.pdf\n")
cat("✅ Saved: results/figure2_fedremove_escalation.png\n\n")

# --------------------------------------------------------------------------- #
# Generate summary statistics table
# --------------------------------------------------------------------------- #

cat("Generating summary statistics...\n")

summary_stats <- w2_tbl %>%
  group_by(scenario) %>%
  summarise(
    retrain_w2 = mean(w2_distance[method == "retrain"]),
    fedremove_w2 = mean(w2_distance[method == "FedRemove"]),
    ratio = fedremove_w2 / retrain_w2,
    .groups = "drop"
  ) %>%
  mutate(
    scenario = recode(scenario, !!!setNames(scenario_labels, scenario_levels))
  )

print(summary_stats)

# Save as CSV for reference
write_csv(w2_tbl, file.path(output_dir, "w2_distances_all.csv"))
cat("✅ Saved: results/w2_distances_all.csv\n\n")

# --------------------------------------------------------------------------- #
# Print summary
# --------------------------------------------------------------------------- #

cat("\n" , rep("=", 80), "\n", sep = "")
cat("ANALYSIS COMPLETE\n")
cat(rep("=", 80), "\n\n", sep = "")

cat("Generated files:\n")
cat("  LaTeX Tables:\n")
cat("    - table1_w2_distances.tex (W2 by scenario)\n")
cat("    - table2_fedremove_detail.tex (FedRemove comparison)\n")
cat("    - table3_method_rankings.tex (Method rankings)\n")
cat("  Figures:\n")
cat("    - figure1_w2_comparison.pdf/png (Main comparison)\n")
cat("    - figure2_fedremove_escalation.pdf/png (FedRemove escalation)\n")
cat("  Data:\n")
cat("    - w2_distances_all.csv (All W2 distances)\n\n")

cat("Key Findings:\n")
for (i in 1:nrow(summary_stats)) {
  s <- summary_stats[i, ]
  cat(sprintf("  %s: FedRemove W2 = %.4f, Retrain W2 = %.4f, Ratio = %.1fx\n",
              s$scenario, s$fedremove_w2, s$retrain_w2, s$ratio))
}

cat("\n✅ Ready for LaTeX compilation!\n")

