#!/bin/bash

# Cleanup script for FooocusPlus
# This script will remove temporary files, caches, and other unnecessary files

echo "Starting cleanup..."

# 1. Remove Python cache files
echo "Removing Python cache files..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find . -type f -name "*.py[co]" -delete

# 2. Remove Python virtual environment caches
echo "Clearing Python caches..."
if [ -d "venv" ]; then
    find venv -type d -name "__pycache__" -exec rm -rf {} +
    find venv -type f -name "*.py[co]" -delete
fi

# 3. Remove temporary files
echo "Removing temporary files..."
find . -type f -name "*.tmp" -delete
find . -type f -name "*.swp" -delete
find . -type f -name "*.swo" -delete
find . -type f -name ".DS_Store" -delete

# 4. Clean up package caches
echo "Cleaning package caches..."
if command -v pip &> /dev/null; then
    pip cache purge
fi

# 5. Remove any empty directories
echo "Removing empty directories..."
find . -type d -empty -delete 2>/dev/null

# 6. Clean up any remaining temporary directories
echo "Cleaning up temporary directories..."
if [ -d "/var/folders/vw/5rq1y8yn3535q0r9661292d00000gn/T/fooocus" ]; then
    rm -rf "/var/folders/vw/5rq1y8yn3535q0r9661292d00000gn/T/fooocus"
fi

# 7. Remove any leftover extraction files
rm -f "SupportPack.7z" 2>/dev/null

# 8. Clean up logs and temporary output files
echo "Cleaning logs and output files..."
find . -type f -name "*.log" -delete
find . -type f -name "*.log.*" -delete

# 9. Remove the cleanup script itself
echo "Cleanup complete!"
echo "You can now delete this cleanup script with: rm cleanup.sh"

echo "Cleanup finished successfully!"

# Show disk usage after cleanup
echo -e "\nCurrent disk usage:"
df -h .
