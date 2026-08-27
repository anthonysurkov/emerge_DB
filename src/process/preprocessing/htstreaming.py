import subprocess
from pathlib import Path
from collections.abc import Iterator


def stream_htstream(
    script: Path,
    infile_r1: Path,
    infile_r2: Path,
    primer_5p: str,
    primer_3p: str,
    min_length: int = 50,
    max_length: int = 150
) -> Iterator[list[str]]:
    proc = subprocess.Popen(
        [
            "bash", script,
            infile_r1, infile_r2,
            primer_3p, primer_5p,
            str(min_length), str(max_length)
        ],
        stdout=subprocess.PIPE,
        text=True,
    )
    assert proc.stdout is not None
    try:
        for line in proc.stdout:
            yield line.rstrip("\n").split("\t")
    finally:
        proc.stdout.close()

        returncode = proc.wait()
        if returncode != 0:
            raise subprocess.CalledProcessError(returncode, script)
