from core.files import FileHandle
from collections import deque
from typing import Callable
import inspect

class DataHandle:
    def __init__(self, fh: FileHandle):
        self.fh = fh
        self.jobs = deque()
        self.log: list[str] = []

    def queue_method(self, method: Callable) -> None:
        signature = inspect.signature(method)
        if "file" not in signature.parameters:
            raise ValueError(f"Signature does not contain `file` argument "
                f"for following job:\n"
                f"{method.__name__}{signature}"
            )
        self.jobs.append(method)

    def run_pipeline(self) -> None:
        while len(self.jobs) > 0:
            job = self.jobs.popleft()
            job_id = job(file=self.fh.path)
            self.log.append(job_id)

