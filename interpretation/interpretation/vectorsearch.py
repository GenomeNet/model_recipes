import faiss
import numpy as np
import pandas as pd
import argparse
import os
from BCBio import GFF
import matplotlib.pyplot as plt

def build_index(input_file, output_file):
    df = pd.read_csv(input_file, skiprows=1)
    data = np.ascontiguousarray(df.values.astype('float32'))
    faiss.normalize_L2(data)
    dimension = data.shape[1]
    quantizer = faiss.IndexFlatL2(dimension)
    nlist = 50
    index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
    assert not index.is_trained
    index.train(data)
    assert index.is_trained
    index.nprobe = 50
    index.add(data)
    faiss.write_index(index, output_file)

def extract_vector(input_file, position, output_file):
    df = pd.read_csv(input_file, skiprows=1)
    vector = df.iloc[position-1].values
    pd.DataFrame(vector).to_csv(output_file, index=False, header=["Value"])

def compute_similarity(index, query_vector):
    similarities, indices = index.search(query_vector, index.ntotal)
    similarity_tuples = [(i, s) for i, s in zip(indices[0], similarities[0])]
    return similarity_tuples

def parse_gff(gff_file):
    features = {}
    with open(gff_file, 'r') as file:
        for rec in GFF.parse(file):
            for feature in rec.features:
                start = int(feature.location.start) + 1
                end = int(feature.location.end)
                feature_type = feature.type
                description = feature.qualifiers.get("product", [""])[0]
                features[(start, end)] = (feature_type, description)
    return features

def get_annotation(position, features):
    for (start, end), (feature_type, description) in features.items():
        if start <= position <= end:
            return feature_type, description
    return "NA", "NA"


def plot(data_file, output_file):
    df = pd.read_csv(data_file)
    
    # Round the values
    df['Similarity'] = df['Similarity'].round(2)
    
    fig, ax = plt.subplots()
    
    # Plot a line graph with reduced line width
    ax.plot(df['Position'], df['Similarity'], linestyle='-', marker='', color='b', linewidth=0.7)
    
    # Hide x-axis labels and set x-axis label
    ax.set_xticks([])
    ax.set_xlabel("Genome Position")
    ax.set_ylabel("Similarity")
    
    # Configure grid and layout
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    plt.tight_layout()
    
    # Save to the specified output file
    plt.savefig(output_file, format='pdf')
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query tool for indexing, extracting, and searching vectors.")
    
    subparsers = parser.add_subparsers(dest="command")

    # Indexing parser
    index_parser = subparsers.add_parser('index')
    index_parser.add_argument("--input", type=str, required=True, help="Path to the input CSV file.")
    index_parser.add_argument("--output", type=str, required=True, help="Path to the output index file.")
    
    # Extracting parser
    extract_parser = subparsers.add_parser('extract')
    extract_parser.add_argument("--input", type=str, required=True, help="Path to the input CSV file.")
    extract_parser.add_argument("--position", type=int, required=True, help="Row number to extract.")
    extract_parser.add_argument("--output", type=str, required=True, help="Path to the output file where vector will be saved.")
    
    # Searching parser
    search_parser = subparsers.add_parser('search')
    search_parser.add_argument("--input", type=str, required=True, help="Path to the index file.")
    search_parser.add_argument("--query", type=str, required=True, help="Path to the query vector CSV.")
    search_parser.add_argument("--gff", type=str, help="Path to the GFF file for annotation.")
    search_parser.add_argument("--output", type=str, required=True, help="Path to the output file where results will be saved.")

    # Add the "plot" parser
    plot_parser = subparsers.add_parser('plot')
    plot_parser.add_argument("data_file", type=str, help="Path to the data file (CSV).")
    plot_parser.add_argument("--output", type=str, required=True, help="Path to the output PDF file.")

    args = parser.parse_args()

    if args.command == "index":
        build_index(args.input, args.output)
    elif args.command == "extract":
        extract_vector(args.input, args.position, args.output)
    
    elif args.command == "plot":
        plot(args.data_file, args.output)

    elif args.command == "search":
        # Load the saved index
        index = faiss.read_index(args.input)
        # Load the query vector
        query_vector = pd.read_csv(args.query, header=0)["Value"].values.reshape(1, -1).astype('float32')
        faiss.normalize_L2(query_vector)
        
        # Compute similarities
        results = compute_similarity(index, query_vector)

        # If GFF file is provided, parse it
        features = {}
        if args.gff:
            features = parse_gff(args.gff)

        # Print the top 5 results to the screen without sorting
        print("\nTop 5 Similarities:")
        for position, value in results[:5]:
            rounded_value = round(value, 2)
            feature_type, description = get_annotation(position+1, features)
            
            annotation = ""
            if feature_type != "NA":
                annotation = f" | {feature_type} (product={description})"
            else:
                annotation = " (no overlapping feature)"

            print(f"Position {position + 1} ({rounded_value}){annotation}")

        # Sort results based on row number (position) for writing to file
        sorted_results = sorted(results, key=lambda x: x[0])

        # Write all results to the output file with added annotations
        with open(args.output, 'w') as file:
            file.write("Position,Similarity,Feature Type,Description\n")  # Header line
            for position, value in sorted_results:
                feature_type, description = get_annotation(position+1, features)
                description = description.replace(",", ";")
                file.write(f"{position + 1},{value},{feature_type},{description}\n")