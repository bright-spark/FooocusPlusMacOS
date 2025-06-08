#!/bin/bash

# Optimizations for Intel MacBook Pro 2019 with 16GB RAM
export PYTORCH_MPS_HIGH_WATERMARK_RATIO=0.8
export PYTORCH_ENABLE_MPS_FALLBACK=1
export PYTORCH_MPS_DISABLE_PERFORMANCE_HINTS=1

# Set lower resolution for better performance
export FOOOCUS_DEFAULT_WIDTH=768
export FOOOCUS_DEFAULT_HEIGHT=768

# Disable memory-intensive features
export ENABLE_UPSCALING=false
export ENABLE_FACE_RESTORATION=false

# Reduce memory usage
export ATTENTION_SLICING=true
export ATTENTION_SLICE_SIZE=512

# Use CPU for some operations to reduce VRAM pressure
export USE_CPU=true

# Disable xformers as it's not well supported on Intel Macs
export ENABLE_XFORMERS=false

# Limit the number of workers to reduce memory usage
export NUM_WORKERS=1

# Run FooocusPlus with optimizations
python -m entry_with_update --always-cpu 4 --disable-xformers --disable-metadata --disable-image-log --disable-preset-download --disable-enhance-output-sorting
