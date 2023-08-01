#!/bin/bash

$R CMD INSTALL --build .

# Download the model
wget -P $PREFIX/lib/virusnet https://f000.backblazeb2.com/file/genomenet/models/virus_genus_2023-01-23.hdf5
