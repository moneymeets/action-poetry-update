from pathlib import Path

import click

from actions_helper.commands.update_dependency import update_package


@click.group()
def cli():
    pass


@cli.command(name="dependency-update")
@click.option("--revamp-dir", default=Path.cwd(), type=click.Path(file_okay=False, exists=True, path_type=Path))
def cmd_dependency_update(revamp_dir: Path):
    update_package(revamp_dir=revamp_dir)


if __name__ == "__main__":
    cli()
