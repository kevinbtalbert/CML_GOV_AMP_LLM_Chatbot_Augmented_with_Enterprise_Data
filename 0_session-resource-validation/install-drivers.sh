#!/bin/bash

## Shell script needs at least 16GB to successfully execute.

# Create directory for the NVIDIA installer
mkdir -p /home/cdsw/nvidia-installer

# Download the CUDA installer
curl -o /home/cdsw/nvidia-installer/cuda_12.6.3_560.35.05_linux.run https://developer.download.nvidia.com/compute/cuda/12.6.3/local_installers/cuda_12.6.3_560.35.05_linux.run

# Create the directory to install CUDA
mkdir -p ~/cuda

# Run the CUDA installer
bash /home/cdsw/nvidia-installer/cuda_12.6.3_560.35.05_linux.run --no-drm --no-man-page --override --toolkitpath=$HOME/cuda --toolkit --silent

# Set CUDA environment variables (also need to be set in Project Settings)
export PATH=${PATH}:$HOME/cuda/bin:$HOME/cuda/nvvm
export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:$HOME/cuda/lib64:$HOME/cuda/nvvm/lib64:$HOME/cuda/nvvm
export CUDA_HOME=$HOME/cuda

# Print confirmation
echo "CUDA environment variables set."

# Verify the CUDA installation
echo "Verifying CUDA installation..."
if command -v nvcc &> /dev/null; then
    nvcc --version
    echo "CUDA installation successful!"
else
    echo "CUDA installation failed. Please check your setup."
fi
