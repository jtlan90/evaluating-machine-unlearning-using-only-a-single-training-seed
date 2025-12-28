# NOTE: R must be run from the folder in which this file is located!

library("here")
library("tidyverse")
library("tidyr")
library("magrittr")
library("janitor") # provides clean_names() which converts all column names to snake_case
library("transport") # provides wasserstein1d(x, y, p = 2)


library("tikzDevice")
options(
  tikzDocumentDeclaration = c(
    "\\documentclass[11pt]{article}",
    "\\usepackage{amssymb, amsmath, graphicx, mathtools, mathdots, stmaryrd}",
    "\\usepackage{tikz}"
  )
)

# Default path for saving figures. NOTE: Edit this to to suit your own needs.
fig_path_default <- "/home/axel/Dropbox/Apps/Overleaf/Mini Paper  - Jamie Lanyon/tikz"

fig_type_default <- "tex" # default figure file format

width_default = 2.5 # default figute width
height_default = 2.5 # default figure height

# Saves a figure.
save_figure <- function(
  plot,
  fig_path = fig_path_default,
  fig_name,
  fig_type = fig_type_default,
  width = width_default,
  height = height_default,
  fig_res = "600",
  units = "in",
  onefile = FALSE,
  sleep = 0,
  dev_off = TRUE
) {

  if (dev_off == TRUE) {
    file <- file.path(fig_path, paste0(fig_name, ".", fig_type))
    if (fig_type == "pdf") {
      pdf(file = file, height = height, width = width, onefile = FALSE)
    } else if (fig_type == "png") {
      png(file = file, height = height, width = width, units = units, res = fig_res)
    } else if (fig_type == "tex") {
      tikz(file = file, standAlone = FALSE, width = width, height = height, sanitize = FALSE)
    }
  }
  print(plot)
  Sys.sleep(sleep)
  if (dev_off == TRUE) {
    dev.off()
  }
}

# --------------------------------------------------------------------------- #
# Some auxiliary variables for ensuring consistency across visualisations.
# --------------------------------------------------------------------------- #

# Global parameters:
alpha_fill_default <- 0.1
alpha_retrain <- 0.5
linewidth_retrain <- 0.5
colour_retrain <- "black"

# Names of the unlearning methods as they appear in the data set:
unlearning_method_levels <- c(
  "ssd",
  "lfssd",
  "unsir",
  "bad_teacher",
  "finetune",
  "random_labels",
  "retrain",
  "baseline"
)

# Names of the unlearning methods as they should appear as labels in figures:
unlearning_method_labels <- c(
  "SSD",
  "LFSSD",
  "UNSIR",
  "Bad\nTeacher",
  "Finetune",
  "Random\nLabels",
  "Retrain",
  "Baseline"
)

# Names of the evaluation algorithms as they appear in the data set:
evaluation_algorithm_levels <- c("1", "2")

# Names of the evaluation algorithms as they should appear as labels in figures:
evaluation_algorithm_labels <- c(
  "\\textbf{One training seed}\n(common practice)",
  "\\textbf{Multiple training seeds}\n(our recommendation)"
)

# Names of the data sets as they appear in the data set:
data_set_levels <- c("cifar20", "cifar100")

# Names of the data sets as they should appear as labels in figures:
data_set_labels <- c("CIFAR20", "CIFAR100")

forget_type_levels <- c("full_class", "sub_class")
forget_type_labels <- c("Full-class forgetting", "Sub-class forgetting")

metric_name_levels <- c("retain_accuracy", "forget_accuracy", "test_accuracy", "mia", "zrf")
metric_name_labels <- c("Retain accuracy", "Forget accuracy", "Test accuracy", "MIA", "ZRF")

# --------------------------------------------------------------------------- #
# Read the data into a single data frame ("tibble") in R.
#
# Also extracts some additional information (about the evaluation algorithm
# and the forget type (e.g., full-class or sub-class unlearning) from the
# file names and includes them into the data frame.
# --------------------------------------------------------------------------- #
files <- list.files(here("data"))

data_tbl <- tibble()
for (file in files) {

  file %>%
    str_remove(".csv") %>%
    str_remove("algorithm") %>%
    str_split("-", simplify = TRUE) %>%
    purrr::set_names(
      c("dataset", "net", "forget_type", "aux", "evaluation_algorithm")
    ) -> config

  read_csv(here("data", file)) %>%
    separate_longer_delim(col = Tags, delim = ", ") %>%
    separate_wider_delim(cols = Tags, names = c("key", "value"), delim = ":") %>%
    pivot_wider(names_from = key, values_from = value) %>%
    mutate(evaluation_algorithm = config["evaluation_algorithm"]) %>%
    mutate(forget_type = config["forget_type"]) %>%
    clean_names() -> aux_tbl

  data_tbl %<>% bind_rows(aux_tbl)

}

# --------------------------------------------------------------------------- #
# Store the data as a single tidy data frame ("tibble").
#
# Recall that a data frame is called tidy if each observation is in exactly
# one row and each variable is in exactly one column. Having a tidy structure
# then makes it extremely simple to generate visualisations in ggplot.
#
# The data frame data_tbl obtained from the previous code is not yet tidy
# because the variable "unlearning metric" is spread across multiple columns.
# --------------------------------------------------------------------------- #

data_tbl %<>%
  mutate(data_set = stringr::str_to_lower(dataset)) %>%
  rename("test_accuracy" = "test_acc") %>%
  rename("retain_accuracy" = "retain_test_acc") %>%
  rename("forget_accuracy" = "df") %>%
  pivot_longer( # makes the data frame tidy
    cols = c("test_accuracy", "retain_accuracy", "forget_accuracy", "mia", "zrf"),
    names_to = "metric_name",
    values_to = "metric_value"
  ) %>%
  mutate( # ensures naming consistency
    unlearning_method = dplyr::recode(
      method,
      "UNSIR" = "unsir",
      "blindspot" = "bad_teacher",
      "amnesiac" = "random_labels",
      "ssd_tuning" = "ssd",
      "pdr_tuning" = "ssd",
      "ssd_tuning_loss_free" = "lfssd",
      "pdr_tuning_loss_free" = "lfssd"
    )
  ) %>%
  mutate( # more meaningful names fur the forget types
    forget_type = dplyr::recode(
      forget_type,
      "fc" = "full_class",
      "sc" = "sub_class"
    )
  ) %>%
  mutate(unlearning_method = factor(unlearning_method, levels = unlearning_method_levels)) %>%
  select( # only keep the following variables (columns)
    c(
      unlearning_method, evaluation_algorithm, net, data_set,
      forget_class, forget_type,
      metric_name, metric_value,
      seed
    )
  )

# --------------------------------------------------------------------------- #
# The first figure.
# --------------------------------------------------------------------------- #

unlearning_method_levels_to_plot <- c("ssd", "lfssd", "unsir", "random_labels", "bad_teacher")
retrain_quantile_probabilities <- c(0.25, 0.5, 0.75)

data_tbl %>%
  filter(
    data_set == "cifar100",
    forget_type == "full_class",
    forget_class == "pine",
    metric_name == "retain_accuracy"
  ) -> data_aux_tbl

# Extract retrain (i.e., gold-standard) results to add to the plot:
data_aux_tbl %>%
  filter(unlearning_method == "retrain") %>%
  filter(evaluation_algorithm == 2) %>%
  pull(metric_value) %>%
  quantile(retrain_quantile_probabilities) -> retrain_quantiles

retrain_tbl <- tibble(
  quantile = retrain_quantiles,
  linetype = c("dotted", "solid", "dotted")
)

# The Figure:
data_aux_tbl %>%
  filter(unlearning_method %in% unlearning_method_levels_to_plot) %>%
  ggplot(
    mapping = aes(
      x = unlearning_method,
      y = metric_value,
      fill = evaluation_algorithm,
      colour = evaluation_algorithm
    )
  ) +
  geom_hline(
    data = retrain_tbl,
    mapping = aes(yintercept = quantile, linetype = linetype),
    linewidth = linewidth_retrain,
    colour = colour_retrain,
    alpha = alpha_retrain,
    show.legend = FALSE
  ) +
  geom_boxplot(
    alpha = alpha_fill_default,
    outlier.alpha = 1,
    coef = 1000,
    outlier.shape = NA
  ) +
  theme(
    legend.position = "inside", # this line and the next two move the legend inside the plot region
    legend.position.inside = c(0.95, 0.05), # relative coordinates
    legend.justification = c("right", "bottom"), # anchor point
    legend.margin = margin(-11, -13.5, 0, 1),
    legend.key.height = unit(10, "mm"),
    legend.key.width = unit(6, "mm"),
    legend.text = element_text(margin = margin(5, 0, 5, 0), lineheight = 0.9),
    legend.title = element_text(margin = margin(b = 2)),
    legend.key = element_rect(fill = NA, colour = NA),
    legend.box.background = element_rect(fill = NA, colour = NA)
  ) +
  guides(colour = guide_legend(override.aes = list(size = 2))) +
  labs(x = "Unlearning method", y = "Retain-set accuracy [\\%]", fill = "", colour = "") +
  scale_x_discrete(breaks = unlearning_method_levels, labels = unlearning_method_labels) +
  scale_colour_discrete(breaks = evaluation_algorithm_levels, labels = evaluation_algorithm_labels) +
  scale_fill_discrete(breaks = evaluation_algorithm_levels, labels = evaluation_algorithm_labels) -> fig_1_a

fig_1_a

fig_1_a %>% save_figure(fig_name = "fig_1_a")



data_tbl %>%
  filter(
    data_set == "cifar20",
    forget_type == "sub_class",
    forget_class == "sea",
    metric_name == "forget_accuracy",
  ) -> data_aux_tbl

# Extract retrain (i.e., gold-standard) results to add to the plot:
data_aux_tbl %>%
  filter(unlearning_method == "retrain") %>%
  filter(evaluation_algorithm == 2) %>%
  pull(metric_value) %>%
  quantile(retrain_quantile_probabilities) -> retrain_quantiles

retrain_tbl <- tibble(
  quantile = retrain_quantiles,
  linetype = c("dotted", "solid", "dotted")
)

data_aux_tbl %>%
  filter(unlearning_method %in% unlearning_method_levels_to_plot) %>%
  ggplot(
    mapping = aes(
      x = unlearning_method,
      y = metric_value,
      fill = evaluation_algorithm,
      colour = evaluation_algorithm
    )
  ) +
  geom_hline(
    data = retrain_tbl,
    mapping = aes(yintercept = quantile, linetype = linetype),
    linewidth = linewidth_retrain,
    colour = colour_retrain,
    alpha = alpha_retrain,
    show.legend = FALSE
  ) +
  geom_boxplot(
    alpha = alpha_fill_default,
    outlier.alpha = 1,
    coef = 1000,
    outlier.shape = NA,
    show.legend = FALSE
  ) +
  labs(x = "Unlearning method", y = "Forget-set accuracy [\\%]", fill = "", colour = "") +
  scale_x_discrete(breaks = unlearning_method_levels, labels = unlearning_method_labels) +
  scale_colour_discrete(breaks = evaluation_algorithm_levels, labels = evaluation_algorithm_labels) +
  scale_fill_discrete(breaks = evaluation_algorithm_levels, labels = evaluation_algorithm_labels)-> fig_1_b


fig_1_b %>% save_figure(fig_name = "fig_1_b")



# --------------------------------------------------------------------------- #
# The second figure.
# --------------------------------------------------------------------------- #

data_set_levels_to_plot <- data_set_levels
unlearning_method_levels_to_plot <- c("ssd", "lfssd", "unsir", "bad_teacher", "Finetune", "random_labels")
metric_names_to_plot <- c("retain_accuracy", "forget_accuracy")


wasserstein_tbl <- tibble() # holds the values of the 2-Wasserstein distance

for (u in unlearning_method_levels_to_plot) {
  for (d in data_set_levels_to_plot) {
    for (m in metric_names_to_plot) {

      data_tbl %>%
        filter(
          data_set == d,
          unlearning_method == u,
          metric_name == m
        ) -> data_aux_1_tbl
      data_aux_1_tbl %>% pull(forget_type) %>% unique() -> forget_types

      for (f in forget_types) {

        data_aux_1_tbl %>% filter(forget_type == f) -> data_aux_2_tbl
        data_aux_2_tbl %>% pull(forget_class) %>% unique() -> forget_classes

        for (cl in forget_classes) {

          data_aux_2_tbl %>% filter(forget_class == cl) -> data_aux_3_tbl

          algorithm_1_results <- data_aux_3_tbl %>% filter(evaluation_algorithm == "1") %>% pull(metric_value)
          algorithm_2_results <- data_aux_3_tbl %>% filter(evaluation_algorithm == "2") %>% pull(metric_value)

          wasserstein_tbl %<>% bind_rows(
            tibble(
              data_set = d,
              unlearning_method = u,
              metric_name = m,
              forget_type = f,
              distance = wasserstein1d(algorithm_1_results, algorithm_2_results, p = 2)
            )
          )
        }
      }
    }
  }
}

wasserstein_tbl %>%
  mutate(unlearning_method = factor(unlearning_method, levels = unlearning_method_levels)) %>%
  mutate(
    metric_name = factor(
      metric_name,
      levels = c("retain_accuracy", "forget_accuracy"),
      labels = c("Retain set", "Forget set")
    )
  ) %>%
  mutate(
    data_set = factor(
      data_set,
      levels = data_set_levels,
      labels = data_set_labels
    )
  ) %>%
  mutate(
    forget_type = factor(
      forget_type,
      levels = c("full_class", "sub_class"),
      labels = c("(full class)", "(sub class)")
    )
  ) %>%
  mutate(group = paste0(data_set, "\n", forget_type)) %>%
  ggplot(mapping = aes(x = unlearning_method, y = distance)) +
  facet_grid(
    rows = vars(group),
    cols = vars(metric_name),
    scales = "free"
  ) +
  geom_boxplot(
    coef = 1000,
    outlier.shape = NA
  ) +
  scale_x_discrete(breaks = unlearning_method_levels, labels = unlearning_method_labels) +
  labs(x = "Unlearning method", y = "2-Wasserstein distance\n($I = 1$ vs $I = 11$)") -> fig_2

fig_2

fig_2 %>% save_figure(fig_name = "fig_2", height = 4, width = 4.9)

