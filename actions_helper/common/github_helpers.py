import os
from http import HTTPStatus
from typing import Optional

from github import Github, GithubException, Repository

from .utils import run_process

GIT_REF_PREFIX = "refs/heads/"
BASE_BRANCH_REF = f"{GIT_REF_PREFIX}master"
FEATURE_BRANCH_NAME = "feature/update-python-dependencies"
FEATURE_BRANCH_REF = f"{GIT_REF_PREFIX}{FEATURE_BRANCH_NAME}"

COMMIT_MESSAGE = "chore(poetry): bump dependencies"

GIT_AUTHOR_NAME = "Sir Mergealot"
GIT_AUTHOR_EMAIL = "mergealot@moneymeets.com"


def get_github_repository() -> Repository:
    return Github(login_or_token=os.environ["GITHUB_TOKEN"]).get_repo(
        os.environ["GITHUB_REPOSITORY"],
    )


def configure_git_user(name: str, email: str):
    run_process(f"git config --local user.name '{name}'")
    run_process(f"git config --local user.email '{email}'")


def checkout_remote_feature_branch_or_create_new_local_branch(branch_exists: bool):
    print(
        "Feature branch exists, checking out" if branch_exists else "Feature branch does not exist, creating it",
    )
    run_process(f"git checkout {'' if branch_exists else '-b'} {FEATURE_BRANCH_NAME}")


def check_remote_branch_exists(repo: Repository, branch: str) -> bool:
    try:
        repo.get_branch(branch=branch)
        return True
    except GithubException as e:
        if e.status != HTTPStatus.NOT_FOUND:
            raise
        return False


def modified_files() -> bool:
    return bool(run_process("git diff --quiet", check=False, capture_output=True).returncode)


def commit_and_push_changes(remote_branch_exists: bool):
    print(
        "Adding fixup commit to existing branch" if remote_branch_exists else "Adding commit to newly created branch",
    )
    run_process(f"git commit -a -m '{COMMIT_MESSAGE}'")
    run_process(f"git push --force-with-lease {'' if remote_branch_exists else '-u origin HEAD'}")


def ensure_pull_request_created(repo: Repository, pr_body: Optional[str]):
    print("Checking for pull requests")
    pr = repo.get_pulls(state="open", head=f"{repo.organization.login}:{FEATURE_BRANCH_REF}")

    if pr.totalCount == 0:
        pull_request = repo.create_pull(
            title="Auto bump dependencies",
            body=pr_body if pr_body else "This PR was created automatically. Check the updated dependency changes.",
            base=BASE_BRANCH_REF,
            head=FEATURE_BRANCH_REF,
        )
        print(f"PR <{pull_request.number}> created")
    else:
        pull_request, *_ = tuple(pr)
        pull_request.edit(body=pr_body)
        print(f"Pull request already exists, {pull_request.number}")


def check_and_push_changes(pr_body: str, remote_branch_exists: bool):
    if modified_files():
        print("Found modified files, committing changes")

        repository = get_github_repository()

        commit_and_push_changes(remote_branch_exists=remote_branch_exists)
        ensure_pull_request_created(repo=repository, pr_body=pr_body)

    else:
        print("Nothing changed, skipping this step  ")
