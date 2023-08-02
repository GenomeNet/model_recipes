#!/bin/bash

sed -i '/VIRUSNET_GENUS_MODEL_PATH/d' $PREFIX/etc/conda/activate.d/virusnet.sh
sed -i '/VIRUSNET_GENUS_MODEL_PATH/d' $PREFIX/etc/conda/deactivate.d/virusnet.sh

