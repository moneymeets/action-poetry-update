import click

from actions_helper.commands.update_dependency import get_packages_info, update_packages
from actions_helper.common.github_helpers import (
    FEATURE_BRANCH_REF,
    GIT_AUTHOR_EMAIL,
    GIT_AUTHOR_NAME,
    check_and_push_changes,
    check_remote_branch_exists,
    checkout_remote_feature_branch_or_create_new_local_branch,
    configure_git_user,
    get_github_repository,
)
from actions_helper.common.utils import parse_bool, run_process


@click.group()
def cli():
    pass


@cli.command(name="dependency-update")
@click.option("--dry-run", default="false", type=str)
def cmd_dependency_update(dry_run: str):
    dry_run = parse_bool(dry_run)
    remote_branch_exists = check_remote_branch_exists(repo=get_github_repository(), branch=FEATURE_BRANCH_REF)
    if not dry_run:
        configure_git_user(name=GIT_AUTHOR_NAME, email=GIT_AUTHOR_EMAIL)
        checkout_remote_feature_branch_or_create_new_local_branch(
            branch_exists=remote_branch_exists,
        )
        run_process("git reset --hard origin/master")

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
            remote_branch_exists=remote_branch_exists,
        )


if __name__ == "__main__":
    cli()
