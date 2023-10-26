#!/bin/bash
set -e

mkdir -p $PREFIX/bin

# Install the Python script
echo "Installing the scripts..."
cp $SRC_DIR/vectorsearch.py $PREFIX/bin/vectorsearch

# Make the script executable
chmod +x $PREFIX/bin/vectorsearch