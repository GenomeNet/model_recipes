# Imputation

[![Anaconda-Server Badge](https://anaconda.org/genomenet/imputation/badges/version.svg)](https://anaconda.org/genomenet/imputation)

Imputation is a package that uses machine learning models to classify virus genus based on genomic sequences. The model has been trained on high-quality genomes from the International Committee on Taxonomy of Viruses (ICTV).

### **Installation**

To install Imputation, you can use conda:

```
conda create --name imputation python=3.11
conda activate imputation
```

```
conda install -c genomenet imputation -y
```

### **Usage**

Here's a brief overview of how to use Imputation

```
impute -i <input.fasta> -o <imputed.fasta>
```

**Examples**

Run the tool with custom options, in this case it will perfom a imputation when the probabilty of the imputed nt is abbove 25%:

```
impute -i my_sequences.fasta -o imputed_sequence.fasta -t 0.25
```


