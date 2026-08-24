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

from .regexhelper import prompt_for_regex
from tui.rnatui import RNA_Prompter

REGEX_CHUNK_SIZE  = 10000
TEMPFILE_MAX_SIZE = 5 * 1024**3
OUTDIR            = "regex_temps"

def smart_open(path):
    with open(path, "rb") as f:
        magic = f.read(2)
    if magic == b"\x1f\x8b":  # gzip magic bytes
        return gzip.open(path, "rt", encoding="latin-1")
    return open(path, "r", encoding="latin-1")

def chunk_fastq(path, chunk_size=5000):
    is_gzip = path.endswith(".gz")
    total_size = None if is_gzip else os.path.getsize(path)
    with smart_open(path) as f, tqdm(
        total=total_size, unit="B", unit_scale=True, desc="Reading FASTQ"
    ) as pbar:
        records = []
        while True:
            start_pos = f.tell()
            # Each read = 4 lines
            for _ in range(chunk_size):
                id_line = f.readline()
                if not id_line:
                    break
                seq = f.readline().strip()
                _ = f.readline()
                qual = f.readline().strip()
                records.append((id_line[1:].strip(), seq, qual))
            if not records:
                break
            yield pd.DataFrame(records, columns=["id", "seq", "qual"])
            records = []
            if not is_gzip:
                pbar.update(f.tell() - start_pos)

def regex_match(seq: str, trgt: re.Pattern[str], varb: re.Pattern[str]):
    target_m = trgt.search(seq)
    if not target_m:
        return None, None
    n10_m = varb.search(seq)
    if not n10_m:
        return None, None
    return n10_m.group(1), target_m.group(1)

def save_regex_outputs(
    records: list[tuple[str, str]],
    bytes_processed: int = 0,
    idx: int = 0,
    outdir: str = None
) -> None:
    if not outdir:
        outdir = OUTDIR

    table = pd.DataFrame(records, columns=["n10", "target"])
    ctab = pd.crosstab(table["n10"], table["target"])
    tot = int(ctab.values.sum())

    loc = f"{outdir}/regex_out_{str(idx)}.csv"
    ctab.to_csv(loc)
    print(f"Saved {bytes_processed / 1024**3:.2f} GB of reads to {loc}...")

def run_regex_chunked(
    infile: str,
    trgt: re.Pattern[str],
    varb: re.Pattern[str]
) -> None:
    records = []
    ticker = bytes_so_far = 0
    for df in chunk_fastq(infile, chunk_size=REGEX_CHUNK_SIZE):
        for s in df["seq"]:
            n10, target = regex_match(s, trgt, varb)
            if n10 and target:
                records.append((n10, target))
        chunk_bytes = df["seq"].str.len().sum()
        bytes_so_far += chunk_bytes

        if bytes_so_far >= TEMPFILE_MAX_SIZE:
            save_regex_outputs(
                records=records,
                bytes_processed=bytes_so_far,
                idx=ticker
            )
            records = []
            ticker += 1
            bytes_so_far = 0

    if records:
        save_regex_outputs(
            records=records,
            bytes_processed=bytes_so_far,
            idx=ticker
        )

def collate_regex_chunks(
    unedited: str,
    edited: str,
    minimum_reads: int,
    outdir: str = None
) -> pd.DataFrame:
    if not outdir:
        outdir = OUTDIR
    i = 0
    dfs = []
    while True:
        infile = os.path.join(outdir, f"regex_out_{i}.csv")
        try:
            df = pd.read_csv(infile)
        except FileNotFoundError:
            df = None
        if df is None:
            break
        dfs.append(df)
        i += 1
    if dfs == []:
        print(
            f"Regex service found no dataframes to collate. Likely culprit "
            f"is selected regex itself; no reads found. Double-check selection "
            f"against rawdata sample."
        )
        return None

    df = pd.concat(dfs).groupby("n10").sum().reset_index()
    df = df.rename(columns={"n10": "5to3"})
    df["n"] = df[unedited] + df[edited]
    df["k"] = df[edited]
    df["mle"] = df["k"] / df["n"]
    df = df[df["n"] >= minimum_reads]
    df = df[["5to3", "n", "k", "mle"]]
    df = df.sort_values(by="mle", ascending=False)

    print(f"Collated regex chunks from outdir {outdir} into dataframe...")
    return df

def clean_outdir(outdir: str = None) -> None:
    if not outdir:
        outdir = OUTDIR
    i = 0
    while True:
        infile = os.path.join(outdir, f"regex_out_{i}.csv")
        try:
            os.unlink(infile)
            i += 1
        except FileNotFoundError:
            f"outdir {outdir} cleaned"
            return

def regex_main(
    infile: Path,
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
