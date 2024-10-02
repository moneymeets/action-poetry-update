import click

from actions_helper.commands.update_dependency import get_packages_info, update_packages
from actions_helper.common.github_helpers import check_and_push_changes
from actions_helper.common.utils import parse_bool


@click.group()
def cli():
    pass


@cli.command(name="dependency-update")
@click.option("--dry-run", default="false", type=str)
def cmd_dependency_update(dry_run: str):
    dry_run = parse_bool(dry_run)
    updated_packages = update_packages()
    packages = get_packages_info()

    rendered_message = f"""

#### Updated
```
{updated_packages.strip()}
```

#### Not Updated

After merging this pull request, the following packages will **not** be on the latest version:

```
{packages.strip()}
```
"""
    print(rendered_message)

    if not dry_run:
        print("Commiting to GitHub...")
        check_and_push_changes(
            pr_body=rendered_message,
        )


if __name__ == "__main__":
    cli()
