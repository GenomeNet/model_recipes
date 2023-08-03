#!/usr/bin/env Rscript

# Suppress TF messages
Sys.setenv(TF_CPP_MIN_LOG_LEVEL = 3)

# Load libraries
suppressWarnings(suppressPackageStartupMessages({
  library(deepG)
}))

suppressPackageStartupMessages({
  library(magrittr)
  library(optparse)
  library(ggplot2)
  library(zoo)
})

# Define command line arguments
option_list <- list(
  make_option(c("-i", "--input"), type = "character", default = "test.fasta",
              help = "Input FASTA file."),
  make_option(c("-o", "--output"), type = "character", default = "prediction.csv",
              help = "Output CSV file."),
  make_option(c("-s", "--step"), type = "integer", default = 1000,
              help = "Step size to iterate through sequences [default %default].", metavar = "number"),
  make_option(c("-b", "--batch_size"), type = "integer", default = 32,
              help = "Number of samples processed in one batch [default %default].", metavar = "number")
)

# Parse command line arguments
opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)


# Functions
predict_and_write <- function(opt, model, genus_labels, tmp_file) {
  if (!file.exists(opt$input)) stop("Input file not found")
  
  pred <- predict_model(
    output_format = "one_seq",
    model = model,
    layer_name = "dense_3",
    path_input = opt$input,
    round_digits = 4,
    step = opt$step,
    batch_size = opt$batch_size,
    verbose = FALSE,
    return_states = TRUE,
    padding = "standard",
    mode = "label",
    format = "fasta",
    filename = tmp_file
  )

  df <- data.frame(pred$states)
  names(df) <- genus_labels
  write.table(df, file = opt$output, sep = "\t",
  row.names = FALSE, quote = FALSE)

  return(pred)
}

print_top_predictions <- function(pred) {
  df <- data.frame(pred$states)
  agg <- colMeans(df)
  agg_o <- agg[order(agg, decreasing = TRUE)]
  message("Top 5 predictions of the sample:")
  for (i in 1:5){
    message(paste0("Predicted FASTA sample as ",
    names(agg_o[i]), " (" , round(agg_o[i] * 100, digits = 1), "%)"))
  }
}

model_path <- paste0(Sys.getenv("CONDA_PREFIX"), "/lib/virusnet/virus_genus_2023-01-23.hdf5")
annotation_path <- paste0(Sys.getenv("CONDA_PREFIX"), "/lib/virusnet/virus_genus_2023-01-23_labels.rds")
tmp_file <- tempfile(fileext = ".h5")

# Define paths
model_path <- paste0(Sys.getenv("CONDA_PREFIX"), "/lib/virusnet/virus_genus_2023-01-23.hdf5")
annotation_path <- paste0(Sys.getenv("CONDA_PREFIX"), "/lib/virusnet/virus_genus_2023-01-23_labels.rds")
tmp_file <- tempfile(fileext = ".h5")

# Load model and annotations
message("Loading model and processing file")
if (!file.exists(model_path)) stop("Model file not found")
model <- keras::load_model_hdf5(model_path, compile = FALSE)

message("Loading annotations")
if (!file.exists(annotation_path)) stop("Annotation file not found")
genus_labels <- readRDS(annotation_path)

# Predict
message("Predicting sequence")
pred <- predict_and_write(opt, model, genus_labels, tmp_file)
message("Done")

# Display top 5 predictions
print_top_predictions(pred)

# Cleanup
file.remove(tmp_file)
message(paste0("Wrote predictions to ", opt$output))
