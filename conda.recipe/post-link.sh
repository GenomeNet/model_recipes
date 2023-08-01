#!/bin/bash

echo "export VIRUSNET_GENUS_MODEL_PATH=\$CONDA_PREFIX/lib/virusnet/virus_genus_2023-01-23.hdf5" >> $PREFIX/etc/conda/activate.d/virusnet.sh
echo "unset VIRUSNET_GENUS_MODEL_PATH" >> $PREFIX/etc/conda/deactivate.d/virusnet.sh