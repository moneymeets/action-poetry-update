import subprocess
from pathlib import Path
from typing import Optional


def run_process(command: str, check: bool = True, cwd: Optional[Path] = None):
    print(f"RUNNING {command} - using {cwd}")
    print(subprocess.run(command, capture_output=True, text=True, check=check, shell=True, cwd=cwd).stdout)


def update_package(revamp_dir: Path):
    run_process("pwd")
    run_process("pwd", cwd=revamp_dir)
    run_process("poetry env info", cwd=revamp_dir)
    run_process("poetry env list --full-path", cwd=revamp_dir)
