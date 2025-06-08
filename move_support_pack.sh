#!/bin/bash

# Script to move SupportPack files to their correct locations
# This script will preserve existing files and only move new ones

# Source and destination directories
SRC_DIR="/Users/me/FooocusPlus/SupportPack/UserDir"
DEST_DIR="/Users/me/FooocusPlus/UserDir"

# Create destination directories if they don't exist
mkdir -p "$DEST_DIR"

# Function to move files with rsync (preserves existing files)
move_files() {
    echo "Moving files from $1 to $2..."
    rsync -av --ignore-existing "$1/" "$2/"
    if [ $? -eq 0 ]; then
        echo "Successfully moved files to $2"
    else
        echo "Error moving files to $2"
    fi
}

# Move models directory
if [ -d "$SRC_DIR/models" ]; then
    echo "Processing models directory..."
    mkdir -p "$DEST_DIR/models"
    
    # Move each subdirectory individually
    for dir in "$SRC_DIR/models/"; do
        if [ -d "$dir" ]; then
            dirname=$(basename "$dir")
            echo "Moving $dirname..."
            move_files "$dir" "$DEST_DIR/models/$dirname"
        fi
    done
fi

echo "Support pack files have been moved successfully!"
echo "You can now safely remove the SupportPack directory if everything looks good."
