#!/usr/bin/env python

import faiss
import numpy as np
import pandas as pd
import argparse
import os
from BCBio import GFF
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.backends.backend_pdf import PdfPages

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
                if feature.type == "region":  # Skip the 'region' feature
                    continue
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

def plot_vector(vector_file, output_file):
    # Load the vector data from CSV
    vector = pd.read_csv(vector_file)["Value"].values.reshape(1, -1)

    fig, ax = plt.subplots(figsize=(10, 2))
    
    # Display the heatmap
    cax = ax.imshow(vector, aspect='auto', cmap='viridis', norm=mcolors.Normalize(vmin=-1, vmax=1))
    
    # Hide y-ticks and labels
    ax.set_yticks([])
    ax.set_xlabel('Vector Dimension')
    ax.set_title('1-D Heatmap of Query Vector')
    
    # Add colorbar
    cbar = fig.colorbar(cax, orientation='vertical', pad=0.01)
    cbar.set_label('Value')
    
    plt.tight_layout()
    plt.savefig(output_file, format='pdf')
    plt.show()

import matplotlib.pyplot as plt
import pandas as pd
import matplotlib.colors as mcolors

def plot_similar_vectors(search_output, data_file, output_file):
    # Load the search output data
    df_search = pd.read_csv(search_output)
    
    # Extract data from the input data file
    data = pd.read_csv(data_file, skiprows=1).values.astype('float32')
    
    # Determine the range for the heatmap
    abs_max_value = max(np.abs(data).max(), 1e-10)

    # Sort the DataFrame based on the similarity values
    top_5_positions = df_search.sort_values(by="Similarity", ascending=False).head(5)["Position"].values - 1
    top_similarities = df_search.sort_values(by="Similarity", ascending=False).head(5)["Similarity"].values
    
    # Randomly sample 5 positions (excluding top 5 hits)
    random_positions = df_search.loc[~df_search["Position"].isin(top_5_positions + 1)].sample(5)["Position"].values - 1
    
    # Create a 3-row subplot
    fig, (ax1, ax2, ax3) = plt.subplots(nrows=3, figsize=(12, 15))
    
    # Display heatmap of top 5 hits
    cax1 = ax1.imshow(data[top_5_positions], aspect='auto', cmap='viridis', norm=mcolors.Normalize(vmin=-abs_max_value, vmax=abs_max_value))
    y_labels_top = [f'Hit {i+1} (Similarity: {sim:.2f})' for i, sim in enumerate(top_similarities)]
    ax1.set_yticks(range(len(y_labels_top)))
    ax1.set_yticklabels(y_labels_top)
    ax1.set_title('Top 5 Similar Vectors')
    
    # Add horizontal black lines to separate heatmap rows
    for y in range(1, 5):
        ax1.axhline(y - 0.5, color='black', lw=0.5)
    
    # Highlight the query in the heatmap
    ax1.axhline(0.5, color='black', lw=3)  
    
    # Display heatmap of random vectors
    cax2 = ax2.imshow(data[random_positions], aspect='auto', cmap='viridis', norm=mcolors.Normalize(vmin=-abs_max_value, vmax=abs_max_value))
    y_labels_random = [f'Random {i+1}' for i in range(5)]
    ax2.set_yticks(range(len(y_labels_random)))
    ax2.set_yticklabels(y_labels_random)
    ax2.set_title('5 Random Vectors')
    
    # Add horizontal black lines to separate heatmap rows
    for y in range(1, 5):
        ax2.axhline(y - 0.5, color='black', lw=0.5)
    
    # Overview plot
    ax3.plot(df_search['Position'], df_search['Similarity'], lw=0.5, color='grey', label="Similarity")
    ax3.scatter(random_positions + 1, df_search.loc[df_search["Position"].isin(random_positions + 1), "Similarity"], s=20, c='green', label="Random 5 Hits", zorder=3) 
    ax3.scatter(top_5_positions + 1, top_similarities, s=10, c='red', label="Top 5 Hits")  
    ax3.set_xlabel('Genome Position')
    ax3.set_ylabel('Similarity')
    ax3.legend()
    ax3.set_title('Hits along the genome')
    
    plt.tight_layout()
    plt.savefig(output_file)
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

    # Add the "plotvector" parser
    plotvector_parser = subparsers.add_parser('plotvector')
    plotvector_parser.add_argument("vector_file", type=str, help="Path to the vector file (CSV).")
    plotvector_parser.add_argument("--output", type=str, required=True, help="Path to the output PDF file.")

    # Add the "plotsim" parser
    plotsim_parser = subparsers.add_parser('plotsim')
    plotsim_parser.add_argument("--input", type=str, required=True, help="Path to the search output file (CSV).")
    plotsim_parser.add_argument("--states", type=str, required=True, help="Path to the data file (CSV) containing all vectors.")
    plotsim_parser.add_argument("--output", type=str, required=True, help="Path to the output PDF file.")

    args = parser.parse_args()

    if args.command == "index":
        build_index(args.input, args.output)
    elif args.command == "extract":
        extract_vector(args.input, args.position, args.output)
    
    if args.command == "plotvector":
        plot_vector(args.vector_file, args.output)

    elif args.command == "plot":
        plot(args.data_file, args.output)

    if args.command == "plotsim":
        plot_similar_vectors(args.input, args.states, args.output)

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
        print("\nTop 30 Similarities:")
        for position, value in results[:30]:
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