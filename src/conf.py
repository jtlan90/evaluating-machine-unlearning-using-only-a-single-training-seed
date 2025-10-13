""" 
configurations for this project
"""
"""
This configuration file contains constants and settings used across the SSD project components.
Main configurations include:

- Path definitions for checkpoints and logging
- Class mappings for CIFAR datasets with human-readable label conversions
- Dataset-specific training parameters (epochs, learning rate milestones):
  * PinsFaceRecognition, CIFAR10/20/100 with different training schedules
  * ViT-specific configurations where applicable
- Predefined class subsets for unlearning tasks
- Centralized training constants for experiment reproducibility

These configurations are imported and used by various training scripts, model files, 
and data loaders to maintain consistency across the project.

"""

# Imports here
import os
from datetime import datetime

CHECKPOINT_PATH = "checkpoint"

# Class correspondence as done in https://github.com/vikram2000b/bad-teaching-unlearning
class_dict = {
    "rocket": 69,
    "vehicle2": 19,
    "veg": 4,
    "mushroom": 51,
    "people": 14,
    "baby": 2,
    "electrical_devices": 5,
    "lamp": 40,
    "natural_scenes": 10,
    "sea": 71,
    "42": 42,
    "manmade_objects": 9,
    "fish": 1,
    "fox": 34,
    "pine": 59,
    "1": 1,
    "10": 10,
    "20": 20,
    "30": 30,
    "40": 40,
}

# Caltech101 class mappings (separate from CIFAR classes)
caltech101_class_dict = {
    "airplane": 5,        # airplanes
    "car_side": 19,       # car_side  
    "chair": 22,          # chair
    "elephant": 36,       # elephant
    "face": 0,            # Faces
    "motorbike": 3,       # Motorbikes
    "lamp": 56,           # lamp
    "camera": 17,         # camera
    "umbrella": 93,       # umbrella
    "scissors": 80,       # scissors
}

def get_class_dict(dataset):
    """Get the appropriate class dictionary based on dataset"""
    if dataset == "Caltech101":
        return caltech101_class_dict
    else:
        return class_dict

def get_all_class_choices():
    """Get all available class choices across all datasets"""
    all_choices = set(class_dict.keys()) | set(caltech101_class_dict.keys())
    return list(all_choices)

def get_forget_class_index(dataset, forget_class):
    """Get the class index for the given dataset and forget class"""
    class_dict_to_use = get_class_dict(dataset)
    if forget_class not in class_dict_to_use:
        raise ValueError(f"Class '{forget_class}' not found for dataset '{dataset}'. "
                        f"Available classes: {list(class_dict_to_use.keys())}")
    return class_dict_to_use[forget_class]

# Classes from https://github.com/vikram2000b/bad-teaching-unlearning
cifar20_classes = {"vehicle2", "veg", "people", "electrical_devices", "natural_scenes", "fish", "manmade_objects"}

# Classes from https://github.com/vikram2000b/bad-teaching-unlearning
cifar100_classes = {"rocket", "mushroom", "baby", "lamp", "sea", "fox", "pine"}

# Caltech101 has 101 classes - here are some representative ones for unlearning experiments  
caltech101_classes = {"airplane", "car_side", "chair", "elephant", "face", "motorbike", "lamp", "camera", "umbrella", "scissors"}

# total training epochs

# Training parameters for the tasks; milestones are when the learning rate gets lowered
PinsFaceRecognition_EPOCHS = 200
PinsFaceRecognition_MILESTONES = [60, 120, 160]

Cifar100_EPOCHS = 200
Cifar100_MILESTONES = [60, 120, 160]

Cifar10_EPOCHS = 20
Cifar10_MILESTONES = [8, 12, 16]

Cifar20_EPOCHS = 40
Cifar20_MILESTONES = [15, 30, 35]

Cifar100_EPOCHS = 200
Cifar100_MILESTONES = [60, 120, 160]

Caltech101_EPOCHS = 70
Caltech101_MILESTONES = [20, 40, 50]

Cifar10_ViT_EPOCHS = 8
Cifar10_ViT_MILESTONES = [7]

Cifar20_ViT_EPOCHS = 9
Cifar20_ViT_MILESTONES = [8]

Cifar100_ViT_EPOCHS = 8
Cifar100_ViT_MILESTONES = [7]

Caltech101_ViT_EPOCHS = 8
Caltech101_ViT_MILESTONES = [7]

DATE_FORMAT = "%A_%d_%B_%Y_%Hh_%Mm_%Ss"
# time of script run
TIME_NOW = datetime.now().strftime(DATE_FORMAT)

# log dir
LOG_DIR = "runs"

# save weights file per SAVE_EPOCH epoch
SAVE_EPOCH = 10
