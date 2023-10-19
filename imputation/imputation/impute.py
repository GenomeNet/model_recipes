#!/usr/bin/env python

import os
import subprocess
import argparse

def run_prediction(input='test.fasta', output='imputed.fasta', batch_size=32, threshold=0.5):
    """
    Function to run the R script for virus imputation using the specified arguments.
    """

    # Define the path to your R script
    r_script_path = os.path.join(os.path.dirname(__file__), "impute.r")

    # Define the command that you would use to run the R script from the command line
    command = ["Rscript", r_script_path, 
           '--input', str(input),
           '--output', str(output),
           '--threshold', str(threshold),
           '--batch_size', str(batch_size)]

    # Run the command
    subprocess.run(command)

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Run nucleotide imputation.')
    parser.add_argument('-i', '--input', type=str, default='input.fasta',
                        help='Input fasta file.')
    parser.add_argument('-o', '--output', type=str, default='imputed.fasta',
                        help='Imputed fasta file.')
    parser.add_argument('-t', '--threshold', type=float, default=0.5,
                        help='Probability threshold at which the imputation will occur.')
    parser.add_argument('-b', '--batch_size', type=int, default=32,
                        help='Number of samples processed in one batch.')

    args = parser.parse_args()

    run_prediction(input=args.input, output=args.output, threshold=args.threshold, batch_size=args.batch_size)
