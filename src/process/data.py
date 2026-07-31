from collections import deque
from typing import Callable, Any
from functools import partial
from dataclasses import dataclass
from datetime import datetime
import inspect

from storage.files import FileHandle


def job_desc(job) -> str:
    if isinstance(job, partial):
        return (
            f"{job.func.__name__}"
            f"(args={job.args!r}, kwargs={job.keywords!r})"
        )
    return job.__name__


@dataclass
class JobLog:
    job: str
    started_at: datetime
    result: Any = None
    error: Exception | None = None


class DataHandle:
    def __init__(self, fh: FileHandle):
        self.fh = fh
        self.jobs: deque[Callable[..., Any]] = deque()
        self.log: list[JobLog] = []

    def queue_method(self, method: Callable, *args, **kwargs) -> None:
        job = partial(method, *args, **kwargs)
        signature = inspect.signature(job)

        if "file" not in signature.parameters:
            name = getattr(method, "__name__", repr(method))
            raise ValueError(
                f"Signature does not contain `file` argument "
                f"for following job:\n{name}{signature}"
            )
        self.jobs.append(job)

    def run_pipeline(self) -> None:
        while self.jobs:
            job = self.jobs.popleft()
            started_at = datetime.now()

            try:
                result = job(file=self.fh.path)
                self.log.append(
                    JobLog(job_desc(job), started_at, result=result)
                )
            except Exception as error:
                self.log.append(
                    JobLog(job_desc(job), started_at, error=error)
                )
                raise # devnote - this should print error, return to main,
                      # and notify user of error via email
