import re

from actions_helper.common.utils import run_process


def get_packages_info() -> str:
    process = run_process("poetry show --outdated --no-ansi", capture_output=True)
    return process.stdout


def update_packages() -> str:
    run_process("pipx upgrade poetry")
    process = run_process("poetry update --no-ansi", capture_output=True)

    return "\n".join(
        [
            line
            for line in process.stdout.split("\n")
            if line
            and (
                line.startswith("Package operations:")
                or re.compile(r"- (Removing|Updating|Installing|Downgrading) .*").match(line.strip())
            )
        ],
    )
