import pandas as pd
from Bio import SeqIO
from itertools import islice
import gzip
import regex
import re
import os
import sys
from tqdm import tqdm
from pathlib import Path

from process.fastq_tooling import smart_open, sample_fastq
from .regexhelper import prompt_for_regex
from tui.rnatui import RNA_Prompter


REGEX_CHUNK_SIZE  = 10000
TEMPFILE_MAX_SIZE = 5 * 1024**3
OUTDIR            = "regex_temps"


def chunk_fastq(infile: Path, chunk_size=10_000) -> Iterator[pd.DataFrame]:
    sample = sample_fastq(infile, size=chunk_size)
    return pd.DataFrame(sample)

def regex_match(seq: str, trgt: re.Pattern[str], varb: re.Pattern[str]):
    target_m = trgt.search(seq)
    if not target_m:
        return None, None
    n10_m = varb.search(seq)
    if not n10_m:
        return None, None
    return n10_m.group(1), target_m.group(1)

def collate_stream(source: Path, :

def regex_main(
    infile: Path,
    regexes: tuple[re.Pattern[str], re.Pattern[str]],
    trgt_unedited: str,
    trgt_edited: str,
    rna_sequence: str,
    minimum_reads: int = 10,
    debug: bool = False
) -> pd.DataFrame:
    response = prompt_for_regex(rna_sequence)
    if response is None:
        return None

    patterns = response[0]
    unedited = response[1]
    edited = response[2]

    run_regex_chunked(infile=infile, trgt=patterns[0], varb=patterns[1])
    df = collate_regex_chunks(unedited, edited, minimum_reads)
    clean_outdir()

    return df

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("infile")
    parser.add_argument("sequence")
    parser.add_argument("--min_reads", type=int, default=10)
    parser.add_argument("--debug", action="store_true")
    args = parser.parse_args()

    path = Path(args.infile)
    if not path.exists():
        raise ValueError("path does not exist")

    regex_main(
        infile=path,
        rna_sequence=args.sequence,
        minimum_reads=args.min_reads,
        debug=args.debug,
    )
