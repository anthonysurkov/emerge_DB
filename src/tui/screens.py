import questionary
from pathlib import Path
from datetime import datetime
from multiprocessing import Process, Queue

import db.interface as database
from process.data import DataHandle, JobLog
from process.entrypoints import (
    processing_sf_raw,
    processing_sf_pre,
    processing_sf_post
)
from tui.session import Session
from tui.styles import MENU_STYLE
from storage.paths import D_ROOT


def valid_date(value: str) -> bool:
    try:
        datetime.fromisoformat(value)
        return True
    except ValueError:
        return False

def prompt_for_target_id() -> str | None:
    tids = database.get_target_ids()
    if not tids:
        print("No target IDs available")
        return None
    response = questionary.select(
        "Select EMERGe target:\n",
        choices=tids,
        style=MENU_STYLE,
    ).ask()
    return response or None

def prompt_for_submission_date() -> str | None:
    while True:
        response = questionary.text(
            "Enter the submission date of the screen for sequencing.\n"
            "Use YYYY-MM-DD.\n"
            "If not recorded, skip this step with Ctrl+C.\n",
            style=MENU_STYLE,
        ).ask()
        if response == None:
            return None
        if valid_date(response):
            return response
        print("Invalid date. Please use YYYY-MM-DD.\n")

def prompt_for_num_reads() -> int | None:
    response = questionary.text(
        "Enter the number of reads ordered for this screen (e.g. 350M).\n",
        style=MENU_STYLE,
    ).ask()
    return response or None

def prompt_for_primers() -> tuple[str, str] | None:
    response1 = questionary.text(
        "Please copy-paste your forward primer sequence (5' to 3').\n",
        style=MENU_STYLE,
    ).ask()
    if not response1:
        return None
    response1 = response1.upper().replace("U","T")
    response2 = questionary.text(
        "Please copy-paste your reverse primer sequence (5' to 3').\n",
        style=MENU_STYLE,
    ).ask()
    if not response2:
        return None
    response1 = response1.upper().replace("U","T")
    return response1, response2

def prompt_for_rawdata_path(label: str) -> Path | None:
    def is_fastq(path: str) -> bool:
        p = Path(path)
        return p.name.endswith(".fastq.gz") or p.name.endswith(".fastq")

    def file_filter(path: str) -> bool:
        p = Path(path)
        return p.is_dir() or is_fastq(path)

    response = questionary.path(
        f"Please select {label} rawdata:",
        default=str(D_ROOT) + "/",
        file_filter=file_filter,
        validate=lambda path: (
            True if is_fastq(path) and Path(path).is_file()
            else "Please select a .fastq or .fastq.gz file."
        ),
        style=MENU_STYLE
    ).ask()
    return response

def prompt_for_rawdata_paths() -> tuple[Path, Path] | None:
    r1 = prompt_for_rawdata_path("R1")
    if r1 is None:
        return None
    while True:
        r2 = prompt_for_rawdata_path("R2")
        if r2 is None:
            return None
        if r2 != r1:
            break
        print("R1 and R2 files cannot be identical.")

    return r1, r2

def prompt_for_entrypoint() -> int:
    print("Please select the entry point for this screen's registration.")
    print("This is where processing will begin from.")
    menu = {
        "Rawdata (R1/R2 downloads)": 0,
        "Preprocessed data (after HTStream)": 1,
        "Processed data (after data mining)": 2,
    }
    choices = [
        questionary.Separator(""),
        "Rawdata (R1/R2 downloads)",
        "Preprocessed data (after HTStream)",
        "Processed data (after data mining)",
        questionary.Separator(""),
    ]
    response = questionary.select(
        message="",
        choices=choices,
        style=MENU_STYLE,
    ).ask()
    return menu[response]

# sf = start_from
def processing_sf_raw(r1_path: Path, r2_path: Path, screen_id) -> bool:
    r1_handle = FileHandle(r1_path)
    r2_handle = FileHandle(r2_path)
    raw_handle = PairedEndHandle(r1_handle, r2_handle)
    pipe = DataHandle(raw_handle)

    pipe.queue_method(preprocessing.htstreaming)
    pipe.queue_method(mining.ngsregex)
    pipe.output("db", screen_id)

def processing_sf_pre() -> bool:
    raise NotImplementedError

def processing_sf_post() -> bool:
    raise NotImplementedError

def register_emerge(session: Session) -> None:
    if not session.is_signed_in:
        print("Please sign in")
        return None

    confirm = False
    while not confirm:
        author: str = session.user # auto
        processing_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # auto

        target_id: str = prompt_for_target_id() # not optional
        if not target_id:
            return
        primers: [str, str] = prompt_for_primers() # not optional
        if not primers:
            return
        forward_primer = primers[0]
        reverse_primer = primers[1]
        rawdata_paths: tuple[Path, Path] = prompt_for_rawdata_paths() # not opt
        if not rawdata_paths:
            return
        r1_path = rawdata_paths[0]
        r2_path = rawdata_paths[1]

        num_reads_ordered: int = prompt_for_num_reads() # optional
        submission_date: str = prompt_for_submission_date() # optional

        print(f"""
            Author: {author}
            Processing date: {processing_date}
            Submission date: {submission_date}
            Target ID: {target_id}
            Forward primer: {forward_primer}
            Reverse_primer: {reverse_primer}
            Rawdata path (R1): {r1_path}
            Rawdata path (R2): {r2_path}
            Reads ordered: {num_reads_ordered}\n
        """)
        confirm = questionary.confirm("Accept?").ask()

    entrypoints = {
        0: lambda: processing_sf_raw(r1_path, r2_path, screen_id),
        1: lambda: processing_sf_pre(screen_id),
        2: lambda: processing_sf_post(screen_id),
    }
    entrypoint = prompt_for_entrypoint()
    if entrypoint is None:
        return None

    screen_id = database.insert_screen_metadata(
        author=author,
        processing_date=processing_date,
        tid=tid,
        forward_primer=forward_primer,
        reverse_primer=reverse_primer,
        r1_path=r1_path,
        r2_path=r2_path,
        num_reads_ordered=num_reads_ordered,
    )
    entrypoints[entrypoint]

    questionary.confirm(
        "EMERGe registration job is now scheduled. If the data is not yet "
        "processed, this might take a while. You may see the status of your "
        "job in the main menu.\n"
        "Press Enter to continue."
    ).ask()

    return
