# ============================================================================ #

# This is deprecated. There should be one file to combine casey and cleaning output tbh
# Dependencies: ShortRead

# ============================================================================ #

library(Biostrings)
library(ShortRead)

# R255XE488Q
# GGGAATGGCGCTTCCCGGCA GGAAGT GAA AAGCTG AGGCCGACTTTCTTTCTTTCGTCG GCCTCA NNNNNNNNNN TCCTGC CGGGTTGTAGGGTC
# Flank indices: (21 through 26), (30 ~ 35), (60 ~ 65), (76 ~ 81)
# N10 region:  (66 ~ 75)
# Edit region: (27 ~ 29)
# Expected:            GGAAGT AAGCTG GCCTCA TCCTGC
# Validation Output:   GGAAGT AAGCTG GCCTCA TCCTGC


# Replace this DNA String with your target.
# Replace expected with the concatenated regions you are selecting for. See
# R255XE488Q example above.
template <- DNAString("GTTTGTACAAAAAAGCAGGCCCTCTCCCAAGTCCACACAGAACGGGGCTGAAAGCCGGGTTTCTTTCTTTCCCCGNNNNNNNNNCCCGTTTGCCCGTAGAGTCGCTGTTCCTGCCATGGAAAATCGATGTTCTT")
expected <- DNAString("CGGGGCTGGCCGGGTCCCCGCCCGTTTG")

# Replace the indices in these lists to adapt the code for a new target.
first_flank  <- list(left=43, right=50)
second_flank <- list(left=54, right=59)
third_flank  <- list(left=70, right=75)
fourth_flank <- list(left=85, right=92)
n10_region   <- list(left=76, right=84)
edit_region  <- list(left=51, right=53)

# Configures bounds on accepted lengths for sequence reads.
size_cdna  <- length(template)
size_left  <- size_cdna - 2
size_right <- size_cdna + 1

# Replace to set input/output file names. input_file must be a .fastq or
# .fastq.gz. output_file must be a .csv.
input_file  <- "r270x_z_chunk.fastq"
outfile     <- "r270x_z_casey_chunk.csv"

# ============================================================================ #

# casey_pipeline()
# Generalized adaptation of Casey's EMERGe pipeline.
# Reference: https://github.com/csjacobsen/EMERGe/blob/bioinformatics/Rstudio%20processing%20R168X
#
casey_pipeline <- function() {
  reads <- readFastq(input_file)
  reads <- reads[width(reads) %in% c(size_left:size_right)]
  
  perfect <- xscat(
    subseq(sread(reads), start = first_flank$left,  end = first_flank$right), 
    subseq(sread(reads), start = second_flank$left, end = second_flank$right), 
    subseq(sread(reads), start = third_flank$left,  end = third_flank$right), 
    subseq(sread(reads), start = fourth_flank$left, end = fourth_flank$right)
  ) == expected
  
  key_seq1 <- subseq(sread(reads)[perfect], edit_region$left, edit_region$right)
  table(key_seq1)
  ks1 <- as.data.frame(table(key_seq1))
  ks1$sample="reads"
  colnames(ks1) <- c("codon", "count", "sample")
  mer_seq1 <- subseq(sread(reads)[perfect], n10_region$left, n10_region$right)
  mk_table <- table((as.character(mer_seq1)),(as.character(key_seq1)))
  write.csv(mk_table, outfile)
}

# validate_hairpin_indices()
# Double checks that the provided indices produce the expected sub sequence.
validate_hairpin_indices <- function(expected) {
  perfect <- paste0(
    subseq(template, first_flank$left, first_flank$right), 
    subseq(template, second_flank$left, second_flank$right), 
    subseq(template, third_flank$left, third_flank$right), 
    subseq(template, fourth_flank$left, fourth_flank$right)
  )
  n10 <- subseq(template, n10_region$left, n10_region$right)
  
  if (perfect != expected) {
    message("validate_hairpin_indices: subsequence does not match expected")
    message(perfect)
    return(FALSE)
  } 
  else if (n10 != DNAString("NNNNNNNNN")) {
    message("validate_hairpin_indices: N10 does not match NNNNNNNNNN")
    message(n10)
    return(FALSE)
  }
  message("validate_hairpin_indices: subsequence indices OK")
  return(TRUE)
}

main <- function() {
  expected <- "CGGGGCTGGCCGGGTCCCCGCCCGTTTG"
  if(!validate_hairpin_indices(expected)) { # (optional check)
    return(FALSE)
  }
  
  casey_pipeline()
  
  message("casey_pipeline.R: done")
  return(TRUE)
}

main()
