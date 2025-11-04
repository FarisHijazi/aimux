"""Tests for ls command."""

from unittest.mock import Mock, patch

from uzi import cmd_ls


class TestGitDiffTotals:
    """Test git diff statistics."""

    @patch("uzi.cmd_ls.subprocess.run")
    @patch("uzi.cmd_ls.StateManager")
    def test_get_git_diff_totals_with_changes(self, mock_sm, mock_run):
        """Test getting diff totals with changes."""
        # Mock state manager to return worktree path
        mock_sm_instance = Mock()
        mock_sm_instance.get_all_states.return_value = {
            "test-session": Mock(worktree_path="/tmp/test"),
        }

        # Mock git command output
        mock_run.return_value = Mock(
            stdout=" 5 files changed, 100 insertions(+), 20 deletions(-)\n",
            returncode=0,
        )

        insertions, deletions = cmd_ls.get_git_diff_totals("test-session", mock_sm_instance)

        assert insertions == 100
        assert deletions == 20

    @patch("uzi.cmd_ls.subprocess.run")
    @patch("uzi.cmd_ls.StateManager")
    def test_get_git_diff_totals_no_changes(self, mock_sm, mock_run):
        """Test getting diff totals with no changes."""
        mock_sm_instance = Mock()
        mock_sm_instance.get_all_states.return_value = {
            "test-session": Mock(worktree_path="/tmp/test"),
        }

        mock_run.return_value = Mock(stdout="", returncode=0)

        insertions, deletions = cmd_ls.get_git_diff_totals("test-session", mock_sm_instance)

        assert insertions == 0
        assert deletions == 0

    @patch("uzi.cmd_ls.subprocess.run")
    @patch("uzi.cmd_ls.StateManager")
    def test_get_git_diff_totals_only_insertions(self, mock_sm, mock_run):
        """Test getting diff totals with only insertions."""
        mock_sm_instance = Mock()
        mock_sm_instance.get_all_states.return_value = {
            "test-session": Mock(worktree_path="/tmp/test"),
        }

        mock_run.return_value = Mock(
            stdout=" 1 file changed, 50 insertions(+)\n",
            returncode=0,
        )

        insertions, deletions = cmd_ls.get_git_diff_totals("test-session", mock_sm_instance)

        assert insertions == 50
        assert deletions == 0


class TestAgentStatus:
    """Test agent status detection."""

    @patch("uzi.cmd_ls.get_pane_content")
    def test_get_agent_status_ready(self, mock_get_content):
        """Test detecting ready status."""
        mock_get_content.return_value = "Agent is ready\n>"

        status = cmd_ls.get_agent_status("test-session")
        assert status == "ready"

    @patch("uzi.cmd_ls.get_pane_content")
    def test_get_agent_status_running(self, mock_get_content):
        """Test detecting running status."""
        mock_get_content.return_value = "Thinking about the problem..."

        status = cmd_ls.get_agent_status("test-session")
        assert status == "running"

    @patch("uzi.cmd_ls.get_pane_content")
    def test_get_agent_status_esc_to_interrupt(self, mock_get_content):
        """Test detecting running status with esc prompt."""
        mock_get_content.return_value = "Processing... esc to interrupt"

        status = cmd_ls.get_agent_status("test-session")
        assert status == "running"

    @patch("uzi.cmd_ls.get_pane_content")
    def test_get_agent_status_error(self, mock_get_content):
        """Test status when pane content can't be retrieved."""
        mock_get_content.return_value = ""

        status = cmd_ls.get_agent_status("test-session")
        assert status == "unknown"


class TestExecuteLs:
    """Test execute_ls command."""

    @patch("uzi.cmd_ls.StateManager")
    def test_execute_ls_no_sessions(self, mock_sm, capsys):
        """Test ls with no active sessions."""
        mock_sm_instance = Mock()
        mock_sm_instance.get_active_sessions_for_repo.return_value = []
        mock_sm.return_value = mock_sm_instance

        cmd_ls.execute_ls()

        captured = capsys.readouterr()
        assert "No active sessions found" in captured.out

    @patch("uzi.cmd_ls.get_agent_status", return_value="ready")
    @patch("uzi.cmd_ls.get_git_diff_totals", return_value=(10, 5))
    @patch("uzi.cmd_ls.StateManager")
    def test_execute_ls_with_sessions(self, mock_sm, mock_diff, mock_status, capsys):
        """Test ls with active sessions."""
        from uzi.state import AgentState

        mock_sm_instance = Mock()
        mock_sm_instance.get_active_sessions_for_repo.return_value = ["agent-test-abc-john"]
        mock_sm_instance.get_all_states.return_value = {
            "agent-test-abc-john": AgentState(
                git_repo="https://github.com/test/repo.git",
                branch_from="main",
                branch_name="john-test-abc-1234",
                prompt="Test prompt",
                worktree_path="/tmp/worktree",
                model="claude",
                port=3000,
                created_at="2024-01-01T00:00:00",
                updated_at="2024-01-01T00:00:00",
            ),
        }
        mock_sm.return_value = mock_sm_instance

        cmd_ls.execute_ls()

        captured = capsys.readouterr()
        assert "AGENT" in captured.out
        assert "john" in captured.out
        assert "claude" in captured.out
