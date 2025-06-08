#!/bin/bash

# Script to MOVE (not copy) SupportPack files to their correct locations
# This will directly move files instead of copying them

# Source and destination directories
SRC_DIR="/Users/me/FooocusPlus/SupportPack/UserDir"
DEST_DIR="/Users/me/FooocusPlus/UserDir"

# Create destination directories if they don't exist
mkdir -p "$DEST_DIR"

# Function to move files with mv
move_files() {
    echo "Moving files from $1 to $2..."
    # Create parent directory structure first
    mkdir -p "$2"
    # Move all files and directories
    mv -n "$1"/* "$2"/ 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "Successfully moved files to $2"
    else
        echo "Error moving files to $2"
    fi
}

# Move models directory
if [ -d "$SRC_DIR/models" ]; then
    echo "Processing models directory..."
    
    # Move each subdirectory individually
    for dir in "$SRC_DIR/models/"; do
        if [ -d "$dir" ]; then
            dirname=$(basename "$dir")
            echo "Moving $dirname..."
            move_files "$dir" "$DEST_DIR/models/$dirname"
        fi
    done
fi

# Clean up empty source directories if they exist
rmdir -p "$SRC_DIR/models" 2>/dev/null

echo "Support pack files have been moved successfully!"
echo "You can now safely remove the SupportPack directory if everything looks good."
