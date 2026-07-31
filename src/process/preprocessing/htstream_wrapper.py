from pathlib import Path
import subprocess


def htstream_auto(
    file: Path,
    project: str,
    primer_3p: str,
    primer_5p: str,
) -> subprocess.CompletedProcess[str]:
    if not isinstance(file, Path):
        raise TypeError("file must be a pathlib.Path")
    if not file.exists():
        raise FileNotFoundError(file)

    working_dir = file if file.is_dir() else file.parent
    script = Path(__file__).with_suffix(".sh")
    command = [
        "bash",
        str(script),
        project,
        primer_3p,
        primer_5p,
    ]
    return subprocess.run(
        command,
        cwd=working_dir,
        check=True,
        text=True,
    )
