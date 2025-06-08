#!/bin/bash

# Create and activate a virtual environment
echo "Creating and activating virtual environment..."
python -m venv venv
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install the updated requirements
echo "Installing updated dependencies..."
pip install -r requirements_versions_updated.txt

# Install any additional dependencies that might be needed
echo "Installing additional dependencies..."
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Verify installations
echo "Verifying installations..."
pip list

echo "\nUpdate complete! Don't forget to activate the virtual environment with 'source venv/bin/activate'"
