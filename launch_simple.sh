#!/bin/bash

# Optimizations for Intel MacBook Pro 2019 with 16GB RAM
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PYTORCH_MPS_DISABLE_PERFORMANCE_HINTS=1

# Set environment variables for better performance
export FOOOCUS_DEFAULT_WIDTH=512
export FOOOCUS_DEFAULT_HEIGHT=512
export ENABLE_UPSCALING=false
export ENABLE_FACE_RESTORATION=false

# Run FooocusPlus with minimal settings
python -m entry_with_update \
    --always-cpu 4 \
    --disable-xformers \
    --disable-metadata \
    --disable-image-log \
    --disable-preset-download \
    --disable-enhance-output-sorting
