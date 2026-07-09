from pathlib import Path

from core.files import FileHandle
from process.data import DataHandle

from prompt_toolkit.formatted_text import HTML
from prompt_toolkit import print_formatted_text
from process.mining.regex.regexhelper import BASE_SYSTEM_PROMPT

print_formatted_text(HTML(BASE_SYSTEM_PROMPT))

"""
def method_one(file: Path) -> str:
    print("method one!")
    return "method_one_id"

def method_two(file: Path) -> str:
    print("method two!")
    return "method_two_id"

test_path = Path("/Users/green/home/work/adar/software/SIMULATION_C_DRIVE")
test_fh = FileHandle(test_path)
test_dh = DataHandle(test_fh)

test_dh.queue_method(method_one)
test_dh.queue_method(method_two)
test_dh.run_pipeline()
log = test_dh.log
print(log)
"""
