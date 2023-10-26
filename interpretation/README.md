# Interprete a deepG model

Will write the neuron responses of a input file when doing infrerence with a genomenet model to an output file for further analysis and interpretation. 

## Usage

### Download models

```
interprete download --model all     # Will download all supported models
```

### Run Inference

```
interprete run \
  -i genome.fasta \                  # Input file
  -o genome_states \                 # Output name (here it will generate a file genome_states_genomenet.csv 
  --model_folder models/ \           # Path to folder where models are located (default: model/ folder)
  --model genomenet \                # Model name
```
