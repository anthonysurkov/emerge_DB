import questionary
from pathlib import Path

import db.interface as database
from process.data import DataHandle, JobLog
from tui.session import Session

# register_emerge needs to fill in screen_metadata then queue up processing
# for either a fastq or csv
# 3 entry points: R1/R2 fastqs, preprocessed fastq, or processed csv
# (1) R1/R2 fastqs should enter at htstream_auto (maybe rename to htstream_casey?)
# or whichever would allow preservation of multiple preprocessing workflows.
# longreads from Natalie's R255X should be included in this system, and the
# method for adding additional workflows ought to be very clear.
# (2) preprocessed fastq should enter at regex
# (3) postprocessed data should just be checked and entered
# all entries that are not (1) need methods selection from methods manager
# so, implement methods manager first

def valid_date(value: str) -> bool | str:
    try:
        date.fromisoformat(value)
        return True
    except ValueError:
        return "Please use YYYY-MM-DD."

def valid_target(value: str) -> bool | str

# R1/R2, preprocessed, or processed == entrypoint
def prompt_for_entrypoint() -> tuple[Path, list[JobLog]]:
    raise NotImplementedError

def register_emerge(session: Session) -> None:
    print("Enter Ctrl+C at any time to abort.")

    targets = database.get_target_ids()
    if not targets:
        print("No targets currently registered.")
        return
    target_id = questionary.select(
        "Please select the screen's target.",
        choices=targets
    ).ask()
    if target_id is None:
        return

    enzyme = questionary.text(
        "Please type in the enzyme used in the screen."
    ).ask()
    if enzyme is None:
        return
    enzyme = enzyme.strip().lower()

    submission_date = questionary.text(
        "Submission date:",
        default=date.today().isoformat(),
        validate=validate_date,
    ).ask()

    # need to fill target_id, author, enzyme, submission_date, num_reads_ordered,
    # primer_seq_5, primer_seq_3, processing_date, rawdata_path
