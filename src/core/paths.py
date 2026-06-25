from pathlib import Path
import yaml

with open("../config.yaml") as f:
    cfg = yaml.safe_load(f)

# config.yaml root
C_ROOT = Path(cfg["paths"]["c_root"])
D_ROOT = Path(cfg["paths"]["d_root"])

# internal
ACTIVE_DIR = C_ROOT
STORAGE_DIR = D_ROOT / "ngs_storage"
