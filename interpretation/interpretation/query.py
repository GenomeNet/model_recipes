import faiss
import numpy as np
import pandas as pd
import argparse
import os
from BCBio import GFF

def compute_similarity(input_file, row_num, fast_search=False):
    """
    Compute cosine similarity between a given row and all other rows.
    
    Parameters:
    - input_file: Path to the CSV file.
    - row_num: Row number to compare with all other rows (0-indexed).
    - fast_search: Whether to use a faster, approximate search method.
    
    Returns:
    - similarity_tuples: A list of tuples containing row indices and their similarity values.
    - query_vector: The vector of the given row.
    - data: Numpy array of the data from the CSV file.
    """
    # Load the CSV file
    try:
        df = pd.read_csv(input_file, skiprows=1)
    except Exception as e:
        print(f"Failed to load CSV file. Error: {e}")
        return [], [], []

    # Convert the DataFrame to a numpy array
    data = np.ascontiguousarray(df.values.astype('float32'))
    
    # Normalize vectors for cosine similarity
    faiss.normalize_L2(data)

    dimension = data.shape[1]

    if fast_search:
        # Use IndexIVFFlat for faster search
        quantizer = faiss.IndexFlatL2(dimension)
        nlist = 50  # determines the number of clusters (or centroids) to create in the vector space
        index = faiss.IndexIVFFlat(quantizer, dimension, nlist, faiss.METRIC_INNER_PRODUCT)
        assert not index.is_trained
        print("Retraining index...")
        index.train(data)
        assert index.is_trained
        index.nprobe = 10  # controls the number of clusters to visit during the search
    else:
        # Use IndexFlatIP for brute-force search
        index = faiss.IndexFlatIP(dimension)

    index.add(data)

    # Compute similarity
    query_vector = data[row_num].reshape(1, -1)
    similarities, indices = index.search(query_vector, data.shape[0])
    
    # Pair each similarity score with its row number
    similarity_tuples = [(i, s) for i, s in zip(indices[0], similarities[0])]

    # Exclude the queried row
    similarity_tuples = [tup for tup in similarity_tuples if tup[0] != row_num]

    return similarity_tuples, query_vector, data

def parse_gff(gff_file):
    """
    Parse the provided GFF file to extract features using BioPython's GFF parser.
    
    Parameters:
    - gff_file: Path to the GFF file.
    
    Returns:
    - features: A dictionary with start and end positions as keys and features as values.
    """
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
    """
    Retrieve annotation for a given position from the parsed GFF features.
    
    Parameters:
    - position: The position to annotate.
    - features: The parsed GFF features.
    
    Returns:
    - (feature_type, description): A tuple containing the feature type and description.
    """
    for (start, end), (feature_type, description) in features.items():
        if start <= position <= end:
            return feature_type, description
    return "NA", "NA"

if __name__ == "__main__":

    # Argument parsing
    parser = argparse.ArgumentParser(description="Compute cosine similarity using FAISS.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input CSV file.")
    parser.add_argument("--position", type=int, required=True, help="Row number to compare with all other rows.")
    parser.add_argument("--output", type=str, required=True, help="Path to the output file where results will be saved.")
    parser.add_argument("--gff", type=str, help="Path to the GFF file for annotation.")
    parser.add_argument("--fast-search", action="store_true", 
                        help="Use a faster, approximate search instead of brute force.")
    
    args = parser.parse_args()

    # Check file validity
    if not os.path.exists(args.input):
        print(f"File {args.input} does not exist.")
        exit(1)

    if not os.path.isfile(args.input):
        print(f"{args.input} is not a valid file.")
        exit(1)

    # Additional check to ensure CSV format
    if not args.input.endswith('.csv'):
        print(f"{args.input} might not be a CSV file as it doesn't have a .csv extension.")
        exit(1)

    # Adjust the position to match 0-based indexing
    row_num = args.position - 1

    # Providing feedback to the user
    print("Computing similarities...")
    
    # Call the compute_similarity function
    results, query_vector, data = compute_similarity(args.input, row_num, args.fast_search)

    # If GFF file is provided, parse it
    features = {}
    if args.gff:
        features = parse_gff(args.gff)

    # Handle the potential issue of --position being out of bounds
    if not results:
        print(f"Error: Position {args.position} is out of bounds or there was an issue processing the CSV.")
        exit(1)
    
    # Print the query vector with truncation for high-dimensional data
    if len(query_vector[0]) > 10:
        print(f"Query Vector (Position {args.position}): {query_vector[0][:5]} ... {query_vector[0][-5:]}")
    else:
        print(f"Query Vector (Position {args.position}): {query_vector[0]}")
    
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

    print("Writing output...")
     # Write all results to the output file with added annotations
    with open(args.output, 'w') as file:
        file.write("Position,Similarity,Feature Type,Description\n")  # Header line
        for position, value in sorted_results:
            feature_type, description = get_annotation(position+1, features)
            file.write(f"{position + 1},{value},{feature_type},{description}\n")



