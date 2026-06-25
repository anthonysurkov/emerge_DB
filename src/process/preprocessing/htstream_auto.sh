#!/usr/bin/env bash

# Author: Anthony Surkov (anthonysurkov@gmail.com)
# Aug 24, 2025

# Config
PROJ="$1"
PRIMER_3P="$2"
PRIMER_5P="$3"

if [[ -z ${4-} ]]; then
	RECIP_BOOL="false"
else
	RECIP_BOOL="true"
	RECIPIENT=$4
fi
[[ -z ${1-} ]] && {
	echo "error: missing project name (arg 1). To use htstream_automator, please enter: htstream_auto [project name] [3' primer sequence] [5' primer sequence] [email (optional)]" >&2; exit 1; 
}
[[ -z ${2-} ]] && {
	echo "error: missing 3' primer sequence (arg 3) To use htstream_automator, please enter: htstream_auto [project name] [3' primer sequence] [5' primer sequence] [email (optional)]" >&2; exit 1; 
}
[[ -z ${3-} ]] && {
	echo "error: missing 5' primer sequence (arg 4) To use htstream_automator, please enter: htstream_auto [project name] [3' primer sequence] [5' primer sequence] [email (optional)]" >&2; exit 1; 
}

if [ -d "$(pwd)/input" ]; then
	echo "error: input directory already exists. Please make sure you're running htstream_auto in the correct directory."
	exit 1
fi
if [ -d "$(pwd)/mid" ]; then
	echo "error: mid directory already exists. Please make sure you're running htstream_auto in the correct directory."
	exit 1
fi
if [ -d "$(pwd)/output" ]; then
	echo "error: output directory already exists. Please make sure you're running htstream_auto in the correct directory."
	exit 1
fi

mkdir "$(pwd)/input"
mkdir "$(pwd)/mid"
mkdir "$(pwd)/output"
mv "$(pwd)"/*_R1_* "$(pwd)/input/"
mv "$(pwd)"/*_R2_* "$(pwd)/input/"

if [ $RECIP_BOOL = "true" ]; then
	echo "$RECIPIENT will be contacted when the job is complete."
fi
echo "Running HT Stream preprocessing steps for ${PROJ}."
echo "Please do not close this terminal instance!"
echo "Enter ctrl+C at any time to abort process."

# HT Stream steps
# 1
hts_Stats \
	--stats-file "./output/${PROJ}.log" \
	--notes 'compute stats on original dataset' \
	--read1-input "./input"/*_R1_* \
	--read2-input "./input"/*_R2_* \
	-f "./mid/${PROJ}_Stats"
echo "HTS Stats done! (1 of 7)"
# 2
hts_SeqScreener \
	--append-stats-file "./output/${PROJ}.log" --notes 'remove Phix' \
	--read1-input "./mid"/*Stats_R1.fastq.gz \
	--read2-input "./mid"/*Stats_R2.fastq.gz \
	--check-read-2 \
	-f "./mid/${PROJ}_Seq"
echo "HTS SeqScreener done! (2 of 7)"
# 3
hts_Overlapper \
	--append-stats-file "./output/${PROJ}.log" --notes 'Overlap reads' \
	--read1-input "./mid"/*Seq_R1.fastq.gz \
	--read2-input "./mid"/*Seq_R2.fastq.gz \
	-f "./mid/${PROJ}_Over"
echo "HTS Overlapper done! (3 of 7)"
# 4
hts_Primers \
	--append-stats-file "./output/${PROJ}.log" --notes 'ID proper amplicons' \
	-U "./mid"/*Over*SE* \
	--primers_5p ${PRIMER_5P} \
	--primers_3p ${PRIMER_3P} \
	--keep --flip \
	-f "./mid/${PROJ}_Primer"
echo "HTS Primers done! (4 of 7)"
# 5
hts_NTrimmer \
	--append-stats-file "./output/${PROJ}.log" --notes 'remove N characters' \
	-U "./mid"/*Primer*SE* \
	--exclude \
	-f "./mid/${PROJ}_Trimmer"
echo "HTS NTrimmer done! (5 of 7)"
# 6
hts_LengthFilter \
	--append-stats-file "./output/${PROJ}.log" --notes 'remove too short/long seqs' \
	-U "./mid"/*Trimmer*SE* --min-length 50 --max-length 150 --no-orphans \
	-f "./mid/${PROJ}_Length"
echo "HTS LengthFilter done! (6 of 7)"
# 7
hts_Stats \
	--append-stats-file "./output/${PROJ}.log" --notes 'final stats' \
	-U "./mid"/*Length*SE* --force \
	--fastq-output "./output/${PROJ}_preprocessed"
echo "HTS Stats done! (7 of 7)"

if [ $RECIP_BOOL = "true" ]; then
	SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
	python3 "${SCRIPT_DIR}/emailer.py"
fi

