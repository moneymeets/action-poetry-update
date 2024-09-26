import logging
import subprocess
from pathlib import Path


def run_process(command: str, check: bool = True, capture_output: bool = False, cwd: Path = None):
    logging.info(f"RUNNING {command}")
    return subprocess.run(command, check=check, shell=True, text=True, capture_output=capture_output, cwd=cwd)


def parse_bool(value: str) -> bool:
    return value.lower() in ["true", "t", "1"]
