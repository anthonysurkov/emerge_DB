from pathlib import Path
import subprocess


def htstream_auto(
    read1: Path,
    read2: Path,
    primer_3p: str,
    primer_5p: str,
) -> subprocess.CompletedProcess[str]:
    if not isinstance(read1, Path):
        raise TypeError("file must be a pathlib.Path")
    if not isinstance(read2, Path):
        raise TypeError("file must be a pathlib.Path")
    if not read1.exists():
        raise FileNotFoundError(file)
    if not read2.exists():
        raise FileNotFoundError(file)

    r1_namepieces = read1.name.split("_R1")
    r2_namepieces = read2.name.split("_R2")
    proj = r1_namepieces[0]
    r2_proj = r2_namepieces[0]
    if proj != r2_proj:
        raise ValueError(
            "Read pair has mismatched project names: "
            f"R1 file {read1.name!r} identifies project {proj!r}, "
            f"but R2 file {read2.name!r} identifies project {r2_proj!r}."
        )

    working_dir = file if file.is_dir() else file.parent
    script = Path(__file__).with_suffix(".sh")
    command = [
        "bash",
        str(script),
        proj,
        primer_3p,
        primer_5p,
    ]
    return subprocess.run(
        command,
        cwd=working_dir,
        check=True,
        text=True,
    )
