#!/bin/bash
set -e

# Functional test
impute -i ${PREFIX}/tests/test.fasta -o ${PREFIX}/tests/output.fasta

# Verify output file exists
if [ ! -f "${PREFIX}/tests/output.fasta" ]; then
    echo "Output file not found."
    exit 1
fi
