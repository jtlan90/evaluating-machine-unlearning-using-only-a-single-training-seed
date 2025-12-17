# This is the main file to run all experiments
# Bash file to run different seeds (corresponding to the value) across all tasks
# Pass the GPU ID with the first parameter (e.g., 0; check via nvidia-smi)

#!/bin/bash
#set -e # uncomment to make the script stop when an error occurs; otherwise will ignore
DEVICE=$1  # Changed from $0 to $1 to correctly get the first argument

# Pre-train the model resnet18 on CIFAR10, CIFAR20, CIFAR100, CIFAR20 with subclasses
# python pretrain_model.py -net resnet18 -dataset Cifar10 -classes 10 -gpu
# python pretrain_model.py -net resnet18 -dataset Cifar20 -classes 20 -gpu
# python pretrain_model.py -net resnet18 -dataset Cifar100 -classes 100 -gpu
# python pretrain_model.py -net resnet18 -dataset Cifar20 -classes 100 -gpu

# # Pre-train the model resnet18 on PinsFaceRecognition
# python pretrain_model.py -net resnet18 -dataset PinsFaceRecognition -classes 105 -gpu

# # Pre-train the model ViT on CIFAR10, CIFAR20, CIFAR100, CIFAR20 with subclasses
# python pretrain_model.py -net ViT -dataset Cifar10 -classes 10 -gpu
# python pretrain_model.py -net ViT -dataset Cifar20 -classes 20 -gpu
# python pretrain_model.py -net ViT -dataset Cifar100 -classes 100 -gpu
# python pretrain_model.py -net ViT -dataset Cifar20 -classes 100 -gpu

# TODO: Set the range for the number of seeds you want to run. Value is used as seed
# TODO: Do not forget to set the paths to the model weights in the other bash files (e.g., cifar20_fullclass_exps.sh)
# You might encounter issues with executing this file due to different line endings with Windows and Unix. Use dos2unix "filename" to fix.



for value in {100..100}
do  
    # ResNet18
    python pretrain_model.py -net ResNet18 -dataset Cifar20 -classes 20 -gpu -seed $value
    ./cifar20_fullclass_exps.sh $DEVICE $value
    ./cifar20_subclass_exps.sh $DEVICE $value

    python pretrain_model.py -net ResNet18 -dataset Cifar100 -classes 100 -gpu -seed $value
    ./cifar100_fullclass_exps.sh $DEVICE $value


    # # ViT
    # python pretrain_model.py -net ViT -dataset Cifar20 -classes 20 -gpu -seed $value
    # ./cifar20_fullclass_exps_vit.sh $DEVICE $value
    # ./cifar20_subclass_exps_vit.sh $DEVICE $value

    # python pretrain_model.py -net ViT -dataset Cifar100 -classes 100 -gpu -seed $value
    # ./cifar100_fullclass_exps_vit.sh $DEVICE $value

    
   
done
