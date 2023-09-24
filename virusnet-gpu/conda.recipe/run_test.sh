#!/bin/bash

virusnet -i ${PREFIX}/tests/test.fasta -o ${PREFIX}/tests/output.csv

# Check if the output file is created
if [ -f "${PREFIX}/tests/output.csv" ]; then
    echo "Output file created successfully."
else
    echo "Output file not found."
    exit 1
fi
