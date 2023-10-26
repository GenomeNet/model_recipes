# Perform vectorsearch on a GenomeNet mode

Will write the neuron responses of a input file when doing infrerence with a genomenet model to an output file for further analysis and interpretation.

## Requirements

### This software requires the output of the interprete package (see https://anaconda.org/GenomeNet/interpretation). Please run this first to generate the csv file.

## Installation

```
conda install -c genomenet vectorsearch -y
```

## Usage

First, index the output csv file of the `interprete run` command

```
vectorsearch index --input genome_states_genomenet.csv --output genome_states_genomenet.index
```

Then extract the vector of the position you want to search/visualize later

```
vectorsearch extract --input genome_states_genomenet.csv --position 655515 --output extracted_vector.csv
```

Now, perform the search using this extracted vector and the index. You can supply a gff file to automatically annotate the hits

```
vectorsearch search --input genome_states_genomenet.index --query extracted_vector.csv --output output.csv --gff file.gff
```

The 30 top hits will be written to the screen

```
Top 30 Similarities:
Position 655515 (1.0) | direct_repeat (product=)
Position 1105116 (0.9300000071525574) | gene (product=)
Position 655494 (0.9300000071525574) (no overlapping feature)
Position 655575 (0.9300000071525574) | direct_repeat (product=)
Position 520308 (0.9300000071525574) | gene (product=)
Position 520281 (0.9300000071525574) | gene (product=)
Position 1253865 (0.9300000071525574) | gene (product=)
Position 593433 (0.9300000071525574) | gene (product=)
Position 1704186 (0.9300000071525574) (no overlapping feature)
Position 1069650 (0.9200000166893005) | gene (product=)
Position 655578 (0.9200000166893005) | direct_repeat (product=)
Position 213999 (0.9200000166893005) | gene (product=)
Position 718687 (0.9200000166893005) | gene (product=)
...
```

Now you can visualize the results

```
vectorsearch plotsim --input output.csv --states genome_states_genomenet.csv --output plot.pdf
```

You can also visualize the query vector

```
vectorsearch plotvector test_vector1.csv --output test_out.pdf
```
