#!/usr/bin/env Rscript

# Suppress TF messages
Sys.setenv(TF_CPP_MIN_LOG_LEVEL = 3)

# Load libraries
suppressWarnings(suppressPackageStartupMessages({
  library(deepG)
  library(magrittr)
  library(optparse)
  library(ggplot2)
  library(zoo)
}))

# Define command line arguments
option_list <- list(
  make_option(c("-i", "--input"), type = "character", default = "test.fasta",
              help = "Input FASTA file."),
  make_option(c("-o", "--output"), type = "character", default = "prediction",
              help = "Prefix for the output CSV file. Model name will be appended."),
  make_option(c("-m", "--model"), type = "character", default = "genus",
              help = "Name of the model [genus, crispr, genomenet]."), 
  make_option(c("--model_folder"), type = "character", default = "models/", 
              help = "Folder where models are located. Defaults to models/"),
  make_option(c("-s", "--step"), type = "integer", default = 1000,
              help = "Step size to iterate through sequences [default %default].", metavar = "number"),
  make_option(c("-b", "--batch_size"), type = "integer", default = 32,
              help = "Number of samples processed in one batch [default %default].", metavar = "number")
)

# Parse command line arguments
opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)

# Define model paths
model_paths <- list(
  'genus' = paste0(opt$model_folder, "virus_genus_2023-01-23.hdf5"),
  'crispr' = paste0(opt$model_folder, "crispr_binary_model.h5"),
  'genomenet' = paste0(opt$model_folder, "genomenet_intermediate.h5")
)

# Define model layer names
model_layer_names <- list(
  'genus' = "dense_2",
  'crispr' = "dense_1",
  'genomenet' = NULL
)

# Functions
predict_and_write <- function(opt, model, layer_name) {
  if (!file.exists(opt$input)) stop("Input file not found")

  # Use a temporary file for intermediate results
  temp_file <- tempfile()

  pred <- predict_model(
    output_format = "one_seq",
    model = model,
    layer_name = layer_name,
    path_input = opt$input,
    round_digits = 4,
    step = opt$step,
    batch_size = opt$batch_size,
    verbose = FALSE,
    return_states = TRUE,
    padding = "maxlen",
    mode = "label",
    format = "fasta",
    filename = temp_file
  )

  # create states matrix
  pred_list <- load_prediction(temp_file, get_sample_position = TRUE)

  on.exit(file.remove(temp_file), add = TRUE)

  states <- pred_list$states
  states <- states[-1,] # discard first prediction (pred for all zero input)
  
  # Incorporate the model name into the output filename
  output_file <- paste0(opt$output, "_", opt$model, ".csv")
  write.csv(states, file = output_file, row.names = FALSE, quote = FALSE)
  
  message(paste0("Exported state matrix (", nrow(states), " rows and ", ncol(states), " columns) to ", output_file))

}

# Check if the model is supported and get the model path
if (!opt$model %in% names(model_paths)) {
  stop(paste("Unsupported model:", opt$model))
}

model_path <- model_paths[[opt$model]]
layer_name <- model_layer_names[[opt$model]]

# Check if model exists
if (!file.exists(model_path)) {
  stop(paste("Model file not found for", opt$model, "at", model_path))
}

# Load model
model <- load_cp(model_path)

# Predict
message("Predicting sequence")
predict_and_write(opt, model, layer_name)