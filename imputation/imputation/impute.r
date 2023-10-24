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
  make_option(c("-i", "--input"), type = "character", default = "input.fasta",
              help = "Input FASTA file."),
  make_option(c("-o", "--output"), type = "character", default = "output.fasta",
              help = "Imputed FASTA file."),
  make_option(c("-t", "--threshold"), type = "numeric", default = 0.5,
              help = "Threshold [default %default]", metavar = "number"),
  make_option(c("-b", "--batch_size"), type = "integer", default = 32,
              help = "Number of samples processed in one batch [default %default].", metavar = "number")
)

# Parse command line arguments
opt_parser <- OptionParser(option_list = option_list)
opt <- parse_args(opt_parser)
# Define paths
message(paste0(Sys.getenv("CONDA_PREFIX"), "/lib/impute/bert_bact_150_flatten.h5"))
model_path <- paste0(Sys.getenv("CONDA_PREFIX"), "/lib/impute/bert_bact_150_flatten.h5")
tmp_file <- tempfile(fileext = ".h5")

# Validate the model and annotation paths
if (!file.exists(model_path)) stop("Model file not found")

# Load model and annotations
message("Loading model and processing file")
model <- load_cp(model_path)
# Predict
message("Predicting sequence")

sequence <- microseq::readFasta(opt$input)$Sequence
len <- nchar(sequence)

#### start prediction

maxlen <- 150
message("Processing FASTA file")
pred <- predict_model(vocabulary = c("a", "c", "g", "t", "n"),
                      output_format = "one_seq",
                      model = model,
                      layer_name = "flatten",
                      sequence = sequence,
                      round_digits = 4,
                      filename = NULL,
                      step = maxlen,
                      batch_size = 512,
                      verbose = FALSE,
                      return_states = TRUE,
                      padding = "standard",
                      mode = "label",
                      format = "fasta", 
                      return_int = TRUE)


if (len > maxlen) {
  pred1 <- predict_model(vocabulary = c("a", "c", "g", "t", "n"),
                      output_format = "one_seq",
                      model = model,
                      layer_name = "flatten",
                      sequence = substr(sequence, len - maxlen + 1, len),
                      round_digits = 4,
                      filename = NULL,
                      step = maxlen,
                      batch_size = 4,
                      verbose = FALSE,
                      return_states = TRUE,
                      padding = "standard",
                      mode = "label",
                      format = "fasta",
                      return_int = TRUE)
} else{
  k <- (maxlen - len) * 4
}

num_of_pred <- len %/% maxlen
last_pred <- num_of_pred * maxlen
last_piece <- len %% maxlen
last_addition <- (maxlen - last_piece) * 4
n_positions <- which(strsplit(sequence, "")[[1]] == "N")
orig_ambigous_n <- length(which(strsplit(sequence, "")[[1]] == "N"))
message(paste0("Found ", length(n_positions), " ambiguous nucleotides in the file"))

theshold <- opt$threshold

i <- 1
if (len > maxlen) {
  while (i <= length(n_positions)) {
    j <- n_positions[i]
    j_rem_maxlen <- ((j - 1) %% maxlen) + 1
    if  (j <= last_pred) {
        a <- which.max(pred$state[((j - 1) %/% maxlen) + 1,(j_rem_maxlen * 4 - 3):(j_rem_maxlen * 4)])
        a_prob <- max(pred$state[((j - 1) %/% maxlen) + 1,(j_rem_maxlen * 4 - 3):(j_rem_maxlen * 4)])

      if (a == 1){
          
        if (a_prob >= theshold) {
            substring(sequence, j) <- "A"
             message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'A' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
        } else {
                 message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
        }
          
      } else if (a == 2){
      
        if (a_prob >= theshold) {
            substring(sequence, j) <- "C"
                            message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'C' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
        } else {
                 message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
        }
          
      } else if (a == 3){
       
        if (a_prob >= theshold) {
            substring(sequence, j) <- "G"
                            message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'G' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
        } else {
                 message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
        }
          
      } else if (a == 4){
        
        if (a_prob >= theshold) {
            substring(sequence, j) <- "T"
                            message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'A' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
        } else {
                 message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
        }
          
      } 
    } else {
      a = which.max(pred1$state[1,(last_addition + 
                                   j_rem_maxlen * 4 - 3):(last_addition + j_rem_maxlen * 4)])
      a_prob = which.max(pred1$state[1,(last_addition + 
                                        j_rem_maxlen * 4 - 3):(last_addition + j_rem_maxlen * 4)])

      if (a == 1){
           
            if (a_prob >= theshold) {
                substring(sequence, j) <- "A"
                  message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'A' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
            } else {
                 message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
            }
          
          
      }else if (a == 2){
       
          
            if (a_prob >= theshold) {
                substring(sequence, j) <- "C"
                   message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'C' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
            } else {
                 message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
            }

      }else if (a == 3){
          
          if (a_prob >= theshold) {
            substring(sequence, j) <- "G"
               message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'G' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
        } else {
                 message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
        }
          
      }else if (a == 4){

          if (a_prob >= theshold) {
            substring(sequence, j) <- "T"
               message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'T' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
        } else {
                 message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
        }
      }
    } 
  i <- i + 1
  }
} else {
  while (i <= length(n_positions)) {
    j <- n_positions[i]
    j_rem_maxlen <- ((j - 1) %% maxlen) + 1
    a <- which.max(pred$state[1,(k + j_rem_maxlen * 4 - 3):(k + j_rem_maxlen * 4)])
    a_prob <- which.max(pred$state[1,(k+j_rem_maxlen * 4 - 3):(k+j_rem_maxlen * 4)])
    if (a == 1){
         if (a_prob >= theshold) {
               substring(sequence, j) <- "A"
                 message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'A' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
         } else {
           message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
         }
    
    }else if (a == 2) {
            if (a_prob >= theshold) {
               substring(sequence, j) <- "C"
                 message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'C' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
         } else {
           message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
         }
        
    }else if (a == 3) {
           if (a_prob >= theshold) {
               substring(sequence, j) <- "G"
                 message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'G' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
         } else {
           message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
         }
        
    }else if (a == 4) {
            if (a_prob >= theshold) {
               substring(sequence, j) <- "T"
                 message(paste0("Position " , j, ": Imputing nucleotide 'N' with 'T' (probability ",
                       round(a_prob, digits = 2) * 100, "%)"))
         } else {
           message(paste0("Position " , j, ": Skipping ambiguous nucleotide 'N' since no probability is above threshold"))
         }
        
    }
  i <- i + 1
  }
}

### end prediction
seq <- microseq::readFasta(opt$input)
seq$Sequence <- sequence
microseq::writeFasta(seq, opt$output)
new_ambigous_n <- length(which(strsplit(sequence, "")[[1]] == "N"))

message(paste0("Successfully imputed ", orig_ambigous_n - new_ambigous_n,
               " positions out of ", orig_ambigous_n, " that meet criteria"))
message(paste0("Wrote predictions to ", opt$output))