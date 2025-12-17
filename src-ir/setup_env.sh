#!/bin/bash
# Setup environment for federated learning experiments

echo "=========================================="
echo "Setting up environment for src-ir"
echo "=========================================="

# Create conda environment
echo "Creating conda environment 'foltr' (Federated Online Learning to Rank)..."
conda create --name foltr python=3.8.13 -y

echo ""
echo "=========================================="
echo "Environment 'foltr' created successfully!"
echo "=========================================="
echo ""
echo "To activate the environment and install dependencies, run:"
echo "  conda activate foltr"
echo "  pip install -r requirements.txt"
echo ""
echo "Then you can run experiments with:"
echo "  ./algorithm1.sh  (for Algorithm 1 - training only)"
echo "  ./algorithm2.sh  (for Algorithm 2 - training + unlearning)"
echo ""

