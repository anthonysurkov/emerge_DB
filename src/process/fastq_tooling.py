import gzip
from pathlib import Path
from collections import defaultdict
from collections.abc import Iterator, Iterable
from itertools import islice


def smart_open(path: Path, perm: str = "r") -> None:
    if perm not in ["r","w"]:
        raise ValueError(
            "Invalid smart_open() mode selected; "
            "please use `r` or `w` for `perm` arg"
        )
    with open(path, "rb") as f:
        magic = f.read(2)
    if magic == b"\x1f\x8b":
        return gzip.open(path, perm + "t", encoding="latin-1")
    return open(path, perm + "t", encoding="latin-1")

def stream_fastq(infile: Path) -> Iterator[str, str, str, str]:
    with smart_open(infile, "r") as f:
        while True:
            header = f.readline().rstrip()
            if not header:
                break
            seq = f.readline().rstrip()
            plus = f.readline().rstrip()
            qual = f.readline().rstrip()
            yield header, seq, plus, qual

def write_fastq(
    data: Iterable[tuple[str, str, str, str]],
    outfile: Path
) -> None:
    with open(outfile, "w") as f:
        for record in data:
            f.writelines(f"{s}\n" for s in record)

def sample_fastq(
    infile: Path,
    size: int = 1000
) -> Iterator[str, str, str, str]:
    gen = stream_fastq(infile)
    return islice(gen, size)

