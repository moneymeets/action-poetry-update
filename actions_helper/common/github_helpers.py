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


def check_branch_exists(repo: Repository, branch: str) -> bool:
    try:
        repo.get_branch(branch=branch)
        return True
    except GithubException as e:
        if e.status != HTTPStatus.NOT_FOUND:
            raise
        return False


def modified_files() -> bool:
    return bool(run_process("git diff --quiet", check=False, capture_output=True).returncode)


def commit_and_push_changes(branch_exists: bool):
    print(
        "Adding fixup commit to existing branch" if branch_exists else "Adding commit to newly created branch",
    )
    commit_message = f"fixup! {COMMIT_MESSAGE}" if branch_exists else COMMIT_MESSAGE
    run_process(f"git commit -a -m '{commit_message}'")
    run_process(f"git push {'' if branch_exists else '-u origin HEAD'}")


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


def check_and_push_changes(pr_body: str):
    if modified_files():
        print("Found modified files, committing changes")

        # configure git user
        run_process(f"git config --local user.name '{GIT_AUTHOR_NAME}'")
        run_process(f"git config --local user.email '{GIT_AUTHOR_EMAIL}'")

        repository = get_github_repository()
        branch_exists = check_branch_exists(repo=repository, branch=FEATURE_BRANCH_REF)

        print(
            "Feature branch exists, checking out" if branch_exists else "Feature branch does not exist, creating it",
        )
        run_process(f"git checkout {'' if branch_exists else '-b'} {FEATURE_BRANCH_NAME}")

        commit_and_push_changes(branch_exists=branch_exists)
        ensure_pull_request_created(repo=repository, pr_body=pr_body)
    else:
        print("Nothing changed, skipping this step")
