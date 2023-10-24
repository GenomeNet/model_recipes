#!/bin/bash
set -e

# Download necessary files
#wget -P $PREFIX/lib/impute https://f000.backblazeb2.com/file/bioinf/models/model_imputation_maxlen100.hdf5
wget -P $PREFIX/lib/impute https://f000.backblazeb2.com/file/bioinf/bert_bact_150_flatten.h5

mkdir -p $PREFIX/bin

# Install the Python script
echo "Installing the scripts..."
cp $SRC_DIR/impute.py $PREFIX/bin/impute
cp $SRC_DIR/impute.r $PREFIX/bin/impute.r

# Make the script executable
chmod +x $PREFIX/bin/impute

# Install the R package
echo "Installing the R package from GitHub..."
R -e "devtools::install_github('genomenet/deepg')"
