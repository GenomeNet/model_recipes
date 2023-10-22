#!/usr/bin/env python

import os
import subprocess
import argparse
import requests
import tensorflow as tf

MODEL_URLS = {
    'genus': 'https://f000.backblazeb2.com/file/genomenet/models/virus_genus_2023-01-23.hdf5',
    'crispr': 'https://f000.backblazeb2.com/file/bioinf/crispr_binary_model.h5',
    'genomenet': 'https://f000.backblazeb2.com/file/bioinf/genomenet_intermediate.h5'
}

def model_exists_in_folder(model, model_folder):
    """
    Check if the model exists within the specified folder.
    """
    model_path = os.path.join(model_folder, os.path.basename(MODEL_URLS[model]))
    return os.path.exists(model_path)

def is_valid_fasta(filepath):
    """
    Simple function to check if a file seems to be a valid FASTA format.
    """
    with open(filepath, 'r') as file:
        first_line = file.readline().strip()
        return first_line.startswith(">")
    
def download_model(model_name, destination_folder):
    """
    Function to download the specified hdf5 model.
    """
    # Define the URL to the model
    url = MODEL_URLS[model_name]
    
    # Extract filename from URL
    filename = os.path.basename(url)
    
    # Define the destination path
    destination_path = os.path.join(destination_folder, filename)
    
    # Download the file
    print(f"Downloading {model_name} model...")
    response = requests.get(url, stream=True)
    with open(destination_path, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)
    print(f"{model_name} model downloaded to {destination_path}")


def run_prediction(input='test.fasta', output='states.csv', model='genus', step=1, batch_size=128, model_folder='models'):
    """
    Function to run the R script for interpretation analysis using the specified arguments.
    """

    # Define the path to your R script
    r_script_path = os.path.join(os.path.dirname(__file__), "predict.r")

    # Define the command that you would use to run the R script from the command line
    command = ["Rscript", r_script_path, 
               '--input', input,
               '--output', output,
               '--model', model,
               '--step', str(step),
               '--batch_size', str(batch_size)]

    # Run the command
    subprocess.run(command)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Interpreter tool commands.')
    subparsers = parser.add_subparsers(title="Commands", dest="command")

    # Subparser for the 'download' command
    download_parser = subparsers.add_parser('download', help='Download the hdf5 model.')
    download_parser.add_argument('--model', choices=['genus', 'crispr', 'genomenet', 'all'], required=True, 
                                 help='Which model to download: genus, crispr, genomenet or all.')
    download_parser.add_argument('--model_folder', type=str, default="models", help="Folder to save downloaded models.")

    # Subparser for the 'run' command
    run_parser = subparsers.add_parser('run', help='Run generating neuron states.')
    run_parser.add_argument('-i', '--input', type=str, default='test.fasta', help='Input fasta file.')
    run_parser.add_argument('-o', '--output', type=str, default='states', help='Prefix for the output CSV file. Model name will be appended.')
    run_parser.add_argument('-m', '--model', type=str, default='genus', help='Name of the model [genus, crispr, genomenet].')
    run_parser.add_argument('-s', '--step', type=int, default=1, help='Step size to iterate though sequences.')
    run_parser.add_argument('-b', '--batch_size', type=int, default=128, help='Number of samples processed in one batch.')
    run_parser.add_argument('--model_folder', type=str, default="models", help="Folder where models are located.")

    args = parser.parse_args()

    if args.command == "download":
        if not os.path.exists(args.model_folder):
            os.makedirs(args.model_folder)
        if args.model == "all":
            for model_name in MODEL_URLS:
                download_model(model_name, args.model_folder)
        else:
            download_model(args.model, args.model_folder)

    elif args.command == "run":
        # Check if the input file exists
        if not os.path.exists(args.input):
            print(f"Error: Input file '{args.input}' does not exist!")
            exit(1)

        # Check if the input file seems to be a valid FASTA format
        if not is_valid_fasta(args.input):
            print(f"Error: Input file '{args.input}' does not appear to be a valid FASTA format!")
            exit(1)

        # Check if the model_folder exists
        if not os.path.exists(args.model_folder):
            print(f"Error: Model folder '{args.model_folder}' does not exist!")
            exit(1)

        # Check if the model exists within the model_folder
        if not model_exists_in_folder(args.model, args.model_folder):
            print(f"Error: The specified model '{args.model}' does not exist in the folder '{args.model_folder}'!")
            exit(1)

        run_prediction(input=args.input, output=args.output, step=args.step, model=args.model, batch_size=args.batch_size, model_folder=args.model_folder)
