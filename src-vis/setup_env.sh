#!/bin/bash

# Create and activate conda environment
conda create -n forget python=3.10 -y
conda activate forget

# Install CUDA toolkit and PyTorch with CUDA support
conda install -c conda-forge cudatoolkit=12.1 -y
conda install pytorch torchvision torchaudio pytorch-cuda=12.1 -c pytorch -c nvidia -y

# Install other requirements
pip install numpy matplotlib seaborn pandas scikit-learn tqdm jupyter ipykernel
pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121

echo "Environment setup complete!"
echo "To activate manually later, run: conda activate forget" 