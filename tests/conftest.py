"""Pytest configuration and fixtures."""

import os
import shutil
import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def mock_git_repo(temp_dir, monkeypatch):
    """Create a mock git repository."""
    repo_path = temp_dir / "test_repo"
    repo_path.mkdir()

    # Initialize git repo
    os.chdir(repo_path)
    os.system("git init > /dev/null 2>&1")
    os.system("git config user.email 'test@example.com' > /dev/null 2>&1")
    os.system("git config user.name 'Test User' > /dev/null 2>&1")

    # Create initial commit
    (repo_path / "README.md").write_text("# Test Repo")
    os.system("git add . > /dev/null 2>&1")
    os.system("git commit -m 'Initial commit' > /dev/null 2>&1")

    # Set remote
    os.system(
        "git remote add origin https://github.com/test/test-repo.git > /dev/null 2>&1"
    )

    yield repo_path

    # Cleanup
    os.chdir("/")


@pytest.fixture
def mock_state_dir(temp_dir, monkeypatch):
    """Create a mock state directory."""
    state_dir = temp_dir / "uzi_state"
    state_dir.mkdir(parents=True)

    # Mock the state path
    monkeypatch.setenv("HOME", str(temp_dir))

    return state_dir


@pytest.fixture
def mock_config_file(temp_dir):
    """Create a mock uzi.yaml config file."""
    config_path = temp_dir / "uzi.yaml"
    config_content = """devCommand: npm run dev -- --port $PORT
portRange: 3000-3010
"""
    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def sample_state_data():
    """Sample state data for testing."""
    return {
        "agent-test-abc-john": {
            "git_repo": "https://github.com/test/test-repo.git",
            "branch_from": "main",
            "branch_name": "john-test-abc-1234",
            "prompt": "Test prompt",
            "worktree_path": "/tmp/test/worktree",
            "model": "claude",
            "port": 3000,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-01T00:00:00",
        },
    }
