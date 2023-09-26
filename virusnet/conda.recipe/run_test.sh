#!/bin/bash
set -e

# Functional test
virusnet -i ${PREFIX}/tests/test.fasta -o ${PREFIX}/tests/output.csv

# Verify output file exists
#if [ ! -f "${PREFIX}/tests/output.csv" ]; then
#    echo "Output file not found."
#    exit 1
#fi