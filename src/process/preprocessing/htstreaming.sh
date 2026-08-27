#!/usr/bin/env bash

INFILE_R1="$1"
INFILE_R2="$2"
PRIMER_3P="$3"
PRIMER_5P="$4"
MIN_LENGTH="$5"
MAX_LENGTH="$6"

[[ -z ${1-} ]] && {
	echo "error: missing infile (arg 1). To use htstream_automator, please enter: htstream_auto [project name] [3' primer sequence] [5' primer sequence]" >&2; exit 1;
}
[[ -z ${2-} ]] && {
	echo "error: missing 3' primer sequence (arg 3) To use htstream_automator, please enter: htstream_auto [project name] [3' primer sequence] [5' primer sequence]" >&2; exit 1;
}
[[ -z ${3-} ]] && {
	echo "error: missing 5' primer sequence (arg 4) To use htstream_automator, please enter: htstream_auto [project name] [3' primer sequence] [5' primer sequence]" >&2; exit 1;
}

hts_Stats \
	--stats-file "hts_log.json" \
	--notes 'compute stats on original dataset' \
	--read1-input ${INFILE_R1} \
	--read2-input ${INFILE_R2} \
| hts_SeqScreener \
	--append-stats-file "hts_log.json" \
    --notes 'remove Phix' \
	--check-read-2 \
| hts_Overlapper \
	--append-stats-file "hts_log.json" \
    --notes 'Overlap reads' \
| awk -F '\t' 'NF == 3' \
| hts_Primers \
	--append-stats-file "hts_log.json" \
    --notes 'ID proper amplicons' \
	--primers_5p ${PRIMER_5P} \
	--primers_3p ${PRIMER_3P} \
	--keep --flip \
| hts_NTrimmer \
	--append-stats-file "hts_log.json" \
    --notes 'remove N characters' \
	--exclude \
| hts_LengthFilter \
	--append-stats-file "hts_log.json" \
    --notes 'remove too short/long seqs' \
	--min-length ${MIN_LENGTH} \
    --max-length ${MAX_LENGTH} \
    --no-orphans \
| hts_Stats \
	--append-stats-file "hts_log.json" \
    --notes 'final stats'
