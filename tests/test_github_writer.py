from unittest.mock import MagicMock, patch

import pytest
from github import GithubException

from readme_agent.github_writer import commit_readme

README_CONTENT = "# My Project\n\nA great project.\n"


def make_mock_repo(existing_content: str | None = None, file_sha: str = "abc123"):
    """Build a mock PyGithub repo."""
    mock_repo = MagicMock()

    if existing_content is None:
        # File doesn't exist — get_contents raises 404
        mock_repo.get_contents.side_effect = GithubException(404, {"message": "Not Found"}, None)
    else:
        mock_file = MagicMock()
        mock_file.decoded_content = existing_content.encode("utf-8")
        mock_file.sha = file_sha
        mock_repo.get_contents.return_value = mock_file

    return mock_repo


@patch("readme_agent.github_writer.Github")
def test_creates_file_when_not_exists(MockGithub):
    mock_repo = make_mock_repo(existing_content=None)
    MockGithub.return_value.get_repo.return_value = mock_repo

    result = commit_readme(README_CONTENT, "owner/repo", "README.md", "token", "main")

    assert result is True
    mock_repo.create_file.assert_called_once_with(
        path="README.md",
        message="docs: update README via readme-ai-agent",
        content=README_CONTENT,
        branch="main",
    )


@patch("readme_agent.github_writer.Github")
def test_updates_file_when_content_changed(MockGithub):
    mock_repo = make_mock_repo(existing_content="# Old README\n")
    MockGithub.return_value.get_repo.return_value = mock_repo

    result = commit_readme(README_CONTENT, "owner/repo", "README.md", "token", "main")

    assert result is True
    mock_repo.update_file.assert_called_once()
    call_kwargs = mock_repo.update_file.call_args.kwargs
    assert call_kwargs["content"] == README_CONTENT
    assert call_kwargs["sha"] == "abc123"


@patch("readme_agent.github_writer.Github")
def test_skips_commit_when_content_identical(MockGithub):
    mock_repo = make_mock_repo(existing_content=README_CONTENT)
    MockGithub.return_value.get_repo.return_value = mock_repo

    result = commit_readme(README_CONTENT, "owner/repo", "README.md", "token", "main")

    assert result is False
    mock_repo.update_file.assert_not_called()
    mock_repo.create_file.assert_not_called()


@patch("readme_agent.github_writer.Github")
def test_custom_commit_message(MockGithub):
    mock_repo = make_mock_repo(existing_content=None)
    MockGithub.return_value.get_repo.return_value = mock_repo

    commit_readme(README_CONTENT, "owner/repo", "README.md", "token", "main", commit_message="chore: auto-readme")

    mock_repo.create_file.assert_called_once()
    assert mock_repo.create_file.call_args.kwargs["message"] == "chore: auto-readme"


@patch("readme_agent.github_writer.Github")
def test_raises_on_non_404_github_error(MockGithub):
    mock_repo = MagicMock()
    mock_repo.get_contents.side_effect = GithubException(403, {"message": "Forbidden"}, None)
    MockGithub.return_value.get_repo.return_value = mock_repo

    with pytest.raises(GithubException) as exc_info:
        commit_readme(README_CONTENT, "owner/repo", "README.md", "token", "main")
    assert exc_info.value.status == 403
