from github import Github, GithubException


def commit_readme(
    content: str,
    repo: str,
    path: str,
    token: str,
    branch: str,
    commit_message: str = "docs: update README via readme-ai-agent",
) -> bool:
    """
    Create or update a file in a GitHub repository via the GitHub API.

    Returns True if a commit was made, False if content was identical (no-op).
    Raises GithubException on API errors.
    """
    g = Github(token)
    gh_repo = g.get_repo(repo)

    try:
        existing = gh_repo.get_contents(path, ref=branch)
        # existing.decoded_content returns bytes
        if isinstance(existing, list):
            raise ValueError(f"{path!r} is a directory, not a file")
        current_content = existing.decoded_content.decode("utf-8")
        if current_content == content:
            return False  # idempotent: no change needed
        gh_repo.update_file(
            path=path,
            message=commit_message,
            content=content,
            sha=existing.sha,
            branch=branch,
        )
    except GithubException as e:
        if e.status == 404:
            # File doesn't exist yet — create it
            gh_repo.create_file(
                path=path,
                message=commit_message,
                content=content,
                branch=branch,
            )
        else:
            raise

    return True
