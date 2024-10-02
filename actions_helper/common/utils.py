import subprocess


def run_process(command: str, check: bool = True, capture_output: bool = False):
    print(f"RUNNING {command}")
    process = subprocess.run(command, check=check, shell=True, text=True, capture_output=capture_output)

    if process.returncode != 0:
        print(process.stderr)
        process.check_returncode()

    return process


def parse_bool(value: str) -> bool:
    return value.lower() in ["true", "t", "1"]
