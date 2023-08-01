# Suppress TF messages
Sys.setenv(TF_CPP_MIN_LOG_LEVEL = 3)

# Load libraries
suppressPackageStartupMessages({
  library(deepG)
  library(magrittr)
  library(optparse)
  library(ggplot2)
  library(zoo)
})

# Model path
model_genus_path <- Sys.getenv("VIRUSNET_GENUS_MODEL_PATH")

# Define command line arguments
option_list <- list(
  make_option(c("-m", "--model"), type = "character", default = "genus",
              help = "Model to use (genus/binary).", metavar = "character"),
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

# Ensure model is supported
if (!opt$model %in% c("binary", "genus")) {
  stop("Please select the model via --model. Supported models are currently only 'genus'.")
}

# Process model
if (opt$model == "genus") {
  message("Loading model and processing file")
  
  # Load model and labels
  model <- keras::load_model_hdf5(model_genus_path, compile = FALSE)
  genus_labels <- readRDS("annotations/virus_genus_2023-01-23_labels.rds")

  # Process file
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
    format = "fasta"
  )

  # Create dataframe and write to output
  df <- data.frame(pred$states)
  names(df) <- genus_labels
  write.table(df, file = opt$output, sep = "\t",
  row.names = FALSE, quote = FALSE)

  # Display top 5 predictions
  agg <- colMeans(df)
  agg_o <- agg[order(agg, decreasing = TRUE)]
  message("Top 5 predictions of the sample:")
  for (i in 1:5){
    message(paste0("Predicted FASTA sample as ",
    names(agg_o[i]), " (" , round(agg_o[i] * 100, digits = 1), "%)"))
  }
}
