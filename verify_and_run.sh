#!/bin/bash

# Check if model file exists
if [ ! -f "/Users/me/FooocusPlus/UserDir/models/checkpoints/elsewhereXL_v10.safetensors" ]; then
    echo "Model file not found. Please wait for the download to complete."
    exit 1
fi

# Check if CLIP model files exist
if [ ! -f "/Users/me/FooocusPlus/UserDir/models/clip_vision/clip-vit-large-patch14/config.json" ]; then
    echo "CLIP model files not found. Please download them first."
    exit 1
fi

# Make sure the optimized config exists
if [ ! -f "/Users/me/FooocusPlus/UserDir/config_optimized.txt" ]; then
    echo "Optimized config not found. Please create it first."
    exit 1
fi

# Set environment variables
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PYTORCH_MPS_DISABLE_PERFORMANCE_HINTS=1

# Run FooocusPlus with optimized settings
python -m entry_with_update \
    --always-cpu 4 \
    --disable-xformers \
    --disable-metadata \
    --disable-image-log \
    --disable-preset-download \
    --disable-enhance-output-sorting \
    --config /Users/me/FooocusPlus/UserDir/config_optimized.txt
