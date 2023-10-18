# VirusNet

[![Anaconda-Server Badge](https://anaconda.org/genomenet/virusnet/badges/version.svg)](https://anaconda.org/genomenet/virusnet) [![Anaconda-Server Badge](https://anaconda.org/genomenet/virusnet/badges/latest_release_relative_date.svg)](https://anaconda.org/genomenet/virusnet)

VirusNet is a package that uses machine learning models to classify virus genus based on genomic sequences. The model has been trained on high-quality genomes from the International Committee on Taxonomy of Viruses (ICTV).

### **Installation**

To install VirusNet, you can use conda:

```
conda create --name genomenet_virusnet python=3.11 -y
conda activate genomenet_virusnet
```

```
conda install -c genomenet virusnet -y
```

### **Usage**

Here's a brief overview of how to use VirusNet:

```
virusnet -i <input.fasta> -o <output.csv>
```

#### **Command-Line Options**

- **\-i, --input**: Specifies the input fasta file. (Default: **test.fasta**)
- **\-o, --output**: Specifies the output CSV file where predictions will be saved. (Default: **prediction.csv**)
- **\-s, --step**: Step size to iterate through sequences. (Default: **1000**)
- **\-b, --batch_size**: Number of samples processed in one batch. (Default: **32**)

**Examples**

Run the tool with custom options:

```
virusnet -i my_sequences.fasta -o my_predictions.csv -s 500 -b 64
```


