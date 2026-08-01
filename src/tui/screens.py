from pathlib import Path

from process.data import DataHandle, JobLog

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

# R1/R2, preprocessed, or processed == entrypoint
def prompt_for_entrypoint() -> tuple[Path, list[JobLog]]:
    # foo

def register_emerge():
    # foo
