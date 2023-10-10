#!/bin/bash
set -e

# Download necessary files
wget -P $PREFIX/lib/virusnet https://f000.backblazeb2.com/file/genomenet/models/virus_genus_2023-01-23.hdf5
wget -P $PREFIX/lib/virusnet https://f000.backblazeb2.com/file/genomenet/models/virus_genus_2023-01-23_labels.rds

mkdir -p $PREFIX/bin

# Install the Python script
echo "Installing the scripts..."
cp $SRC_DIR/virusnet.py $PREFIX/bin/virusnet  # copy it to the bin directory
cp $SRC_DIR/predict.r $PREFIX/bin/predict.r  # copy it to the bin directory

# Make the script executable
chmod +x $PREFIX/bin/virusnet

# Install the R package
echo "Installing the R package from GitHub..."
R -e "devtools::install_github('genomenet/deepg')"
