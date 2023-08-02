#!/bin/bash
set -e

mkdir -p $PREFIX/bin

# Install the Python script
echo "Installing the scripts..."
cp $SRC_DIR/virusnet.py $PREFIX/bin/virusnet  # copy it to the bin directory
cp $SRC_DIR/download_model.py $PREFIX/bin/download_model  # copy it to the bin directory
cp $SRC_DIR/predict.r $PREFIX/bin/predict.r  # copy it to the bin directory

# Make the script executable
chmod +x $PREFIX/bin/virusnet
chmod +x $PREFIX/bin/download_model