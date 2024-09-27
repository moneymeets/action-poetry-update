import re
from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional, Sequence

from actions_helper.common.utils import run_process


@dataclass
class PackageInfo:
    package_name: str
    version_installed: str
    version_available: str
    current_hash: Optional[str] = None
    new_hash: Optional[str] = None


@dataclass
class UpdatedPackageInfo:
    package_name: str
    action: Literal["Installing", "Removing", "Updating"]
    version_available: Optional[str] = None
    version_installed: Optional[str] = None


# ?: makes or's | bracket a non-group
VERSION_NUMBER_REGEX = r"\d+\.\d+\.?(?:\*|\d+)?.*"


def get_packages_info(revamp_dir: Path) -> Sequence[PackageInfo]:
    process = run_process(
        "poetry show --latest --top-level --no-ansi",
        capture_output=True,
        cwd=revamp_dir,
    )

    if process.returncode != 0:
        print(process.stderr)
        process.check_returncode()

    # Usually a line conforms to
    # package  current_version    available_version    description
    # cleo     2.1.0   2.1.0  Cleo allows you to create beautiful and testable command-line interfaces.

    # But some line's third column might be the commit hash for GitHub dependencies
    # moneymeets-utils     0.1.0 6268fab 0.1.0 6268fab Common moneymeets Python utilities

    # (!) may be present in the second column to denote not-installed at all packages
    # pydantic-settings         (!) 2.5.2            2.5.2            Settings management using Pydantic

    # split each line by space (1 or more space - doesn't matter)
    line_by_columns = [re.compile(r"\s+").split(line, maxsplit=6) for line in process.stdout.split("\n") if line]

    packages = []

    for column in line_by_columns:
        padding = 0
        if column[1] == "(!)":
            padding = 1

        # if the third column is a version number; then it is the usual case
        if re.compile(VERSION_NUMBER_REGEX).match(column[2 + padding]):
            # if the versions are not outdated, do not append
            if column[1 + padding] != column[2 + padding]:
                packages.append(
                    PackageInfo(
                        package_name=column[0],
                        version_installed=column[1 + padding],
                        version_available=column[2 + padding],
                    ),
                )
        else:
            # if the versions and hash are not outdated, do not append
            if (column[1 + padding] != column[3 + padding]) or (column[2 + padding] != column[4 + padding]):
                packages.append(
                    PackageInfo(
                        package_name=column[0],
                        version_installed=column[1 + padding],
                        current_hash=column[2 + padding],
                        version_available=column[3 + padding],
                        new_hash=column[4 + padding],
                    ),
                )

    return packages


def update_package(dry_run: bool, revamp_dir: Path) -> Sequence[UpdatedPackageInfo]:
    info = run_process("poetry env info", capture_output=True, cwd=revamp_dir)
    print(info.stdout)

    info2 = run_process("poetry env list --full-path", capture_output=True, cwd=revamp_dir)
    print(info2.stdout)

    process = run_process(
        f"poetry update {'--dry-run' if dry_run else ''}",
        capture_output=True,
        cwd=revamp_dir,
    )

    if process.returncode != 0:
        print(process.stderr)
        process.check_returncode()

    line_by_columns = [
        re.compile(r"- (Removing|Updating|Installing) ([^ ]+) \(([^->]+)\s*[->]*\s*([^->]+)?\)").match(line.strip())
        for line in process.stdout.split("\n")
        if line and " - " in line and "Skipped" not in line
    ]

    packages = []

    for column in line_by_columns:
        group = column.groups()
        if group[0] == "Removing":
            packages.append(
                UpdatedPackageInfo(
                    action=group[0],
                    package_name=group[1],
                    version_installed=group[2],
                ),
            )
        elif group[0] == "Installing":
            packages.append(
                UpdatedPackageInfo(
                    action=group[0],
                    package_name=group[1],
                    version_available=group[2],
                ),
            )
        elif group[0] == "Updating":
            packages.append(
                UpdatedPackageInfo(
                    action="Updating",
                    package_name=group[1],
                    version_installed=group[2],
                    version_available=group[3],
                ),
            )

    return packages
