#!/bin/bash

# Activate virtual environment
source venv/bin/activate

# Print current numpy version
echo "Current NumPy version:"
python -c "import numpy; print(numpy.__version__)"

# Downgrade numpy to a stable 1.x version
echo "\nDowngrading NumPy to version 1.26.4..."
pip install numpy==1.26.4

# Verify the installation
echo "\nVerifying NumPy version..."
python -c "import numpy; print('NumPy version:', numpy.__version__)"

echo "\nNumPy has been downgraded. You can now try running the launch script again."
