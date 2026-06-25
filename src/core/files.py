import os
import gzip
import shutil
import filecmp
from pathlib import Path
from core.paths import ACTIVE_DIR, STORAGE_DIR

class FileHandle:
    def __init__(self, path: Path):
        if not path.exists():
            raise ValueError(f"Source filepath does not exist: {path}"
            )
        if path.stat().st_size == 0:
            raise ValueError(f"attempted to link FileHandle to empty file "
                f"{path} (st_size == 0)"
            )
        if not self.write_allowed(ACTIVE_DIR):
            raise ValueError(f"Active directory ({ACTIVE_DIR}) not writable. "
                f"Verify permissions."
            )
        if not self.write_allowed(STORAGE_DIR):
            raise ValueError(f"Storage directory ({STORAGE_DIR}) not writable. "
                f"Verify permissions."
            )
        self.path = path

    @staticmethod
    def write_allowed(destination: Path):
        return os.access(destination, os.W_OK)

    def collides(self, destination: Path, filepath: Path = None):
        if filepath is None:
            filepath = self.path
        if not destination.exists():
            raise ValueError(f"Destination does not exist: {destination}")
        return filepath.name in (f.name for f in destination.iterdir())

    def set_path(self, filepath: Path):
        self.path = filepath

    def zip(self):
        if ".gz" in self.path.suffixes:
            return

        dst = self.path.with_suffix(self.path.suffix + ".gz") # append .gz
        if self.collides(destination=self.path.parent, filepath=dst):
            raise ValueError(f"gzipped version of file already exists in "
                f"target directory {self.path.stem}. Verify paths involved:\n"
                f"{self.path}\n{dst}"
            )
        if not self.write_allowed(dst.parent):
            raise ValueError(f"Target filepath ({dst}) is not write-allowed. "
                f"Check permissions."
            )

        try:
            with open(self.path, "rb") as f_in, gzip.open(dst, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        except Exception:
            dst.unlink(missing_ok=True)
            raise ValueError(f"copyfileobj failed midway during file zipping"
                f". Check if sufficient "
                f"memory in relevant drive. Paths involved:\n"
                f"{self.path}\n{dst}"
            )


        self.path.unlink()
        self.set_path(dst)

    def unzip(self):
        if ".gz" not in self.path.suffixes:
            return

        dst = self.path.with_suffix("") # x.fastq.gz -> x.fastq
        if self.collides(destination=self.path.parent, filepath=dst):
            raise ValueError(f"gzipped version of file already exists in "
                f"target directory ({self.path.stem}). Verify files involved:\n"
                f"{self.path}\n{dst}"
            )
        if not self.write_allowed(dst.parent):
            raise ValueError(f"Target filepath ({dst}) is not write-allowed. "
                f"Check permissions."
            )

        try:
            with gzip.open(self.path, "rb") as f_in, open(dst, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        except Exception:
            dst.unlink(missing_ok=True)
            raise ValueError(f"copyfileobj failed midway during file unzipping"
                f". Check if sufficient "
                f"memory in relevant drive. Paths involved:\n"
                f"{self.path}\n{dst}"
            )


        self.path.unlink()
        self.set_path(dst)

    def move(self, dst: Path):
        self.zip() # returns if already zipped
        if not self.write_allowed(dst.parent):
            raise ValueError(f"Destination file ({dst}) not writable. "
                f"Verify permissions."
            )

        if self.collides(destination=dst.parent, filepath=dst):
            raise ValueError(f"File already exists at destination: {dst}")

        path = self.path
        try:
            with gzip.open(path, "rb") as f_in, gzip.open(dst, "wb") as f_out:
                shutil.copyfileobj(f_in, f_out)
        except Exception:
            dst.unlink(missing_ok=True)
            raise ValueError(f"copyfileobj failed midway during file activation"
                f". Check if sufficient "
                f"memory in relevant drive. Paths involved:\n"
                f"{self.path}\n{dst}"
            )

        if not filecmp.cmp(self.path, dst, shallow=False):
            dst.unlink(missing_ok=True)
            raise ValueError(f"Discrepancy found between copied file and "
                f"original file during file migration from {self.path} to {dst}"
                f" Abort"
            )

        self.path.unlink()
        self.path = dst

    def activate(self):
        if self.path.parent == ACTIVE_DIR:
            return
        if self.collides(ACTIVE_DIR):
            raise ValueError(f"Filepath ({self.path}) collides in active "
                f"directory ({ACTIVE_DIR}). Verify paths involved."
            )

        dst = ACTIVE_DIR / self.path.name
        self.move(dst)

    def inactivate(self):
        if self.path.parent == STORAGE_DIR:
            return
        if self.collides(STORAGE_DIR):
            raise ValueError(f"Filepath ({self.path}) collides in storage "
                f"directory ({STORAGE_DIR}). Verify paths involved."
            )

        dst = STORAGE_DIR / self.path.name
        self.move(dst)


