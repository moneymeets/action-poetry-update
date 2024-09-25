from pathlib import Path

import click

from actions_helper.commands.update_dependency import get_packages_info, update_package
from actions_helper.common.github_helpers import check_and_push_changes
from actions_helper.common.templating import render_string_from_template
from actions_helper.common.utils import parse_bool


@click.group()
def cli():
    pass


@cli.command(name="dependency-update")
@click.option("--dry-run", default="true", type=str)
@click.option("--top-level", default="true", type=str)
@click.option("--reviewers", default="", type=str)
@click.option("--revamp-dir", default=Path.cwd(), type=click.Path(file_okay=False, exists=True, path_type=Path))
def cmd_dependency_update(dry_run: str, reviewers: str, top_level: str, revamp_dir: Path):
    dry_run = parse_bool(dry_run)
    top_level = parse_bool(top_level)
    reviewers = reviewers.split(",") if reviewers else []
    packages = get_packages_info(revamp_dir=revamp_dir)
    updated_packages = update_package(dry_run=dry_run, revamp_dir=revamp_dir)

    rendered_message = render_string_from_template(
        "description.j2",
        context={
            "updated_packages": [
                updated_package
                for updated_package in updated_packages
                if updated_package.package_name in [package.package_name for package in packages]
            ]
            if top_level
            else updated_packages,
            "skipped": [
                package
                for package in packages
                if package.package_name not in [updated_package.package_name for updated_package in updated_packages]
            ],
        },
    )

    if not dry_run:
        print("Revamp: Commiting to GitHub...")
        check_and_push_changes(
            pr_body=rendered_message,
            reviewers=reviewers,
        )
    else:
        print(rendered_message)


if __name__ == "__main__":
    cli()
