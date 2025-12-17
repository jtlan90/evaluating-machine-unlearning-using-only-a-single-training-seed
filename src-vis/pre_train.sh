# This script pre-trains ResNet18 and Vision Transformer (ViT) models on various datasets:
# - CIFAR10 (10 classes)
# - CIFAR20 (20 classes)
# - CIFAR100 (100 classes) 
# - CIFAR20 with subclasses (100 classes)
# - PinsFaceRecognition (105 classes)
#
# The pre-trained models will be used as starting points for various machine unlearning experiments.
# Each model is trained with GPU acceleration enabled.


## Pre-train the model resnet18 on CIFAR10, CIFAR20, CIFAR100, CIFAR20 with subclasses

python pretrain_model.py -net ResNet18 -dataset Cifar10 -classes 10 -gpu
python pretrain_model.py -net ResNet18 -dataset Cifar20 -classes 20 -gpu
python pretrain_model.py -net ResNet18 -dataset Cifar100 -classes 100 -gpu

# Pre-train the model resnet18 on PinsFaceRecognition
# python pretrain_model.py -net resnet18 -dataset PinsFaceRecognition -classes 105 -gpu

# Pre-train the model ViT on CIFAR10, CIFAR20, CIFAR100, CIFAR20 with subclasses
# python pretrain_model.py -net ViT -dataset Cifar10 -classes 10 -gpu
# python pretrain_model.py -net ViT -dataset Cifar20 -classes 20 -gpu
# python pretrain_model.py -net ViT -dataset Cifar100 -classes 100 -gpu
