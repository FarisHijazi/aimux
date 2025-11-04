"""Tests for state management."""

import json
from pathlib import Path
from unittest.mock import Mock, patch

from uzi.state import AgentState, StateManager


class TestAgentState:
    """Test AgentState dataclass."""

    def test_agent_state_creation(self):
        """Test creating an AgentState."""
        state = AgentState(
            git_repo="https://github.com/test/repo.git",
            branch_from="main",
            branch_name="test-branch",
            prompt="Test prompt",
            worktree_path="/tmp/worktree",
            model="claude",
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
            port=3000,
        )

        assert state.git_repo == "https://github.com/test/repo.git"
        assert state.branch_name == "test-branch"
        assert state.port == 3000

    def test_agent_state_default_port(self):
        """Test AgentState with default port value."""
        state = AgentState(
            git_repo="test",
            branch_from="main",
            branch_name="test",
            prompt="test",
            worktree_path="/tmp",
            model="test",
            created_at="2024-01-01T00:00:00",
            updated_at="2024-01-01T00:00:00",
        )
        assert state.port == 0


class TestStateManager:
    """Test StateManager functionality."""

    def test_state_manager_initialization(self, mock_state_dir):
        """Test StateManager initializes correctly."""
        sm = StateManager()
        assert sm.state_path is not None
        assert isinstance(sm.state_path, Path)

    def test_get_active_sessions_no_state_file(self, mock_state_dir):
        """Test getting active sessions when no state file exists."""
        sm = StateManager()
        sessions = sm.get_active_sessions_for_repo()
        assert sessions == []

    @patch("uzi.state.subprocess.run")
    def test_save_state_creates_file(self, mock_run, mock_state_dir):
        """Test that save_state creates state file."""
        # Mock git commands
        mock_run.return_value = Mock(
            stdout="https://github.com/test/repo.git\n", returncode=0
        )

        sm = StateManager()
        sm.save_state(
            prompt="Test prompt",
            branch_name="test-branch",
            session_name="test-session",
            worktree_path="/tmp/worktree",
            model="claude",
            port=3000,
        )

        # Check state file was created
        assert sm.state_path.exists()

        # Check contents
        with open(sm.state_path) as f:
            data = json.load(f)

        assert "test-session" in data
        assert data["test-session"]["prompt"] == "Test prompt"
        assert data["test-session"]["port"] == 3000

    @patch("uzi.state.subprocess.run")
    def test_save_state_updates_existing(
        self, mock_run, mock_state_dir, sample_state_data
    ):
        """Test that save_state updates existing session."""
        mock_run.return_value = Mock(
            stdout="https://github.com/test/repo.git\n", returncode=0
        )

        sm = StateManager()

        # Create initial state
        sm.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sm.state_path, "w") as f:
            json.dump(sample_state_data, f)

        # Update state
        sm.save_state(
            prompt="Updated prompt",
            branch_name="john-test-abc-1234",
            session_name="agent-test-abc-john",
            worktree_path="/tmp/test/worktree",
            model="claude",
            port=3001,
        )

        # Check updated
        with open(sm.state_path) as f:
            data = json.load(f)

        assert data["agent-test-abc-john"]["prompt"] == "Updated prompt"
        assert data["agent-test-abc-john"]["port"] == 3001

    def test_remove_state(self, mock_state_dir, sample_state_data):
        """Test removing a session from state."""
        sm = StateManager()

        # Create initial state
        sm.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sm.state_path, "w") as f:
            json.dump(sample_state_data, f)

        # Remove state
        sm.remove_state("agent-test-abc-john")

        # Check removed
        with open(sm.state_path) as f:
            data = json.load(f)

        assert "agent-test-abc-john" not in data

    def test_get_worktree_info(self, mock_state_dir, sample_state_data):
        """Test getting worktree info for a session."""
        sm = StateManager()

        # Create state file
        sm.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sm.state_path, "w") as f:
            json.dump(sample_state_data, f)

        # Get worktree info
        info = sm.get_worktree_info("agent-test-abc-john")

        assert info is not None
        assert isinstance(info, AgentState)
        assert info.prompt == "Test prompt"
        assert info.port == 3000

    def test_get_worktree_info_nonexistent(self, mock_state_dir):
        """Test getting worktree info for non-existent session."""
        sm = StateManager()

        # Create empty state file
        sm.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sm.state_path, "w") as f:
            json.dump({}, f)

        info = sm.get_worktree_info("nonexistent")
        assert info is None

    def test_get_all_states(self, mock_state_dir, sample_state_data):
        """Test getting all states."""
        sm = StateManager()

        # Create state file
        sm.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sm.state_path, "w") as f:
            json.dump(sample_state_data, f)

        states = sm.get_all_states()

        assert len(states) == 1
        assert "agent-test-abc-john" in states
        assert isinstance(states["agent-test-abc-john"], AgentState)

    def test_get_all_states_empty(self, mock_state_dir):
        """Test getting all states when none exist."""
        sm = StateManager()
        states = sm.get_all_states()
        assert states == {}

    def test_corrupted_state_file_recovery(self, mock_state_dir):
        """Test that corrupted state file is handled gracefully."""
        sm = StateManager()

        # Create corrupted state file
        sm.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sm.state_path, "w") as f:
            f.write("invalid json{{{")

        # Should return empty dict instead of crashing
        states = sm.get_all_states()
        assert states == {}

    @patch("uzi.state.subprocess.run")
    def test_save_state_with_corrupted_file(self, mock_run, mock_state_dir):
        """Test saving state when existing file is corrupted."""
        mock_run.return_value = Mock(
            stdout="https://github.com/test/repo.git\n", returncode=0
        )

        sm = StateManager()

        # Create corrupted state file
        sm.state_path.parent.mkdir(parents=True, exist_ok=True)
        with open(sm.state_path, "w") as f:
            f.write("invalid json")

        # Should create backup and save new state
        sm.save_state(
            prompt="Test",
            branch_name="test",
            session_name="test",
            worktree_path="/tmp",
            model="test",
        )

        # Check backup was created
        backup_path = sm.state_path.with_suffix(".json.backup")
        assert backup_path.exists()

        # Check new state is valid
        with open(sm.state_path) as f:
            data = json.load(f)
        assert "test" in data
