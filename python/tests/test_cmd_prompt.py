"""Tests for prompt command."""

import pytest
from unittest.mock import Mock, patch, call
from uzi import cmd_prompt


class TestPortAvailability:
    """Test port availability checking."""

    @patch('uzi.cmd_prompt.socket.socket')
    def test_is_port_available_true(self, mock_socket):
        """Test checking if port is available."""
        mock_socket_instance = Mock()
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        result = cmd_prompt.is_port_available(3000)
        assert result is True
        mock_socket_instance.bind.assert_called_once_with(("", 3000))

    @patch('uzi.cmd_prompt.socket.socket')
    def test_is_port_available_false(self, mock_socket):
        """Test checking if port is not available."""
        mock_socket_instance = Mock()
        mock_socket_instance.bind.side_effect = OSError("Port in use")
        mock_socket.return_value.__enter__.return_value = mock_socket_instance

        result = cmd_prompt.is_port_available(3000)
        assert result is False

    def test_find_available_port_first_available(self):
        """Test finding first available port."""
        with patch('uzi.cmd_prompt.is_port_available', return_value=True):
            port = cmd_prompt.find_available_port(3000, 3010, [])
            assert port == 3000

    def test_find_available_port_skip_assigned(self):
        """Test finding port skips already assigned ports."""
        def port_checker(port):
            return port not in [3000, 3001]

        with patch('uzi.cmd_prompt.is_port_available', side_effect=port_checker):
            port = cmd_prompt.find_available_port(3000, 3010, [3000, 3001])
            assert port == 3002

    def test_find_available_port_none_available(self):
        """Test when no ports are available."""
        with patch('uzi.cmd_prompt.is_port_available', return_value=False):
            with pytest.raises(RuntimeError, match="No available ports"):
                cmd_prompt.find_available_port(3000, 3001, [])


class TestAgentParsing:
    """Test agent specification parsing."""

    def test_parse_agents_single(self):
        """Test parsing single agent specification."""
        result = cmd_prompt.parse_agents("claude:1")
        assert "claude" in result
        assert result["claude"]["count"] == 1
        assert result["claude"]["command"] == "claude"

    def test_parse_agents_multiple(self):
        """Test parsing multiple agent specifications."""
        result = cmd_prompt.parse_agents("claude:2,codex:3")
        assert len(result) == 2
        assert result["claude"]["count"] == 2
        assert result["codex"]["count"] == 3

    def test_parse_agents_with_spaces(self):
        """Test parsing with whitespace."""
        result = cmd_prompt.parse_agents("claude:1, codex:2")
        assert len(result) == 2

    def test_parse_agents_invalid_format(self):
        """Test parsing invalid format raises error."""
        with pytest.raises(ValueError, match="Invalid agent format"):
            cmd_prompt.parse_agents("invalid")

    def test_parse_agents_invalid_count(self):
        """Test parsing non-integer count raises error."""
        with pytest.raises(ValueError, match="Invalid count"):
            cmd_prompt.parse_agents("claude:abc")

    def test_parse_agents_zero_count(self):
        """Test parsing zero count raises error."""
        with pytest.raises(ValueError, match="Count must be at least 1"):
            cmd_prompt.parse_agents("claude:0")

    def test_parse_agents_negative_count(self):
        """Test parsing negative count raises error."""
        with pytest.raises(ValueError, match="Count must be at least 1"):
            cmd_prompt.parse_agents("claude:-1")


class TestExecutePrompt:
    """Test execute_prompt command."""

    @patch('uzi.cmd_prompt.subprocess.run')
    @patch('uzi.cmd_prompt.get_random_agent', return_value='testbot')
    @patch('uzi.cmd_prompt.StateManager')
    @patch('uzi.cmd_prompt.load_config')
    def test_execute_prompt_basic(self, mock_load_config, mock_state_manager, mock_random, mock_run):
        """Test basic prompt execution without dev server."""
        from uzi.config import Config

        # Mock config with no dev command
        mock_load_config.return_value = Config()

        # Mock git commands
        mock_run.return_value = Mock(
            stdout="abc123\n",
            stderr="",
            returncode=0
        )

        # Mock state manager
        mock_sm_instance = Mock()
        mock_state_manager.return_value = mock_sm_instance

        # Execute prompt
        cmd_prompt.execute_prompt("Test prompt", "claude:1")

        # Verify state was saved
        mock_sm_instance.save_state.assert_called_once()

    @patch('uzi.cmd_prompt.subprocess.run')
    @patch('uzi.cmd_prompt.get_random_agent', return_value='testbot')
    @patch('uzi.cmd_prompt.StateManager')
    @patch('uzi.cmd_prompt.load_config')
    def test_execute_prompt_with_dev_server(self, mock_load_config, mock_state_manager, mock_random, mock_run):
        """Test prompt execution with dev server."""
        from uzi.config import Config

        # Mock config with dev command
        mock_config = Config(
            dev_command="npm run dev -- --port $PORT",
            port_range="3000-3010"
        )
        mock_load_config.return_value = mock_config

        # Mock git commands
        mock_run.return_value = Mock(
            stdout="abc123\n",
            stderr="",
            returncode=0
        )

        # Mock state manager
        mock_sm_instance = Mock()
        mock_state_manager.return_value = mock_sm_instance

        # Mock port availability
        with patch('uzi.cmd_prompt.find_available_port', return_value=3000):
            # Execute prompt
            cmd_prompt.execute_prompt("Test prompt", "claude:1")

            # Verify state was saved with port
            call_args = mock_sm_instance.save_state.call_args
            assert call_args[1]['port'] == 3000

    def test_execute_prompt_empty_prompt(self):
        """Test executing with empty prompt raises error."""
        with pytest.raises(ValueError, match="Prompt argument is required"):
            cmd_prompt.execute_prompt("")

    @patch('uzi.cmd_prompt.subprocess.run')
    @patch('uzi.cmd_prompt.get_random_agent')
    @patch('uzi.cmd_prompt.StateManager')
    @patch('uzi.cmd_prompt.load_config')
    def test_execute_prompt_multiple_agents(self, mock_load_config, mock_state_manager, mock_random, mock_run):
        """Test executing prompt with multiple agents."""
        from uzi.config import Config

        mock_load_config.return_value = Config()
        mock_random.side_effect = ['agent1', 'agent2', 'agent3']
        mock_run.return_value = Mock(stdout="abc123\n", returncode=0)

        mock_sm_instance = Mock()
        mock_state_manager.return_value = mock_sm_instance

        # Execute with multiple agents
        cmd_prompt.execute_prompt("Test prompt", "claude:3")

        # Verify save_state was called 3 times
        assert mock_sm_instance.save_state.call_count == 3


class TestCloneRepository:
    """Test repository cloning functionality."""

    @patch('uzi.cmd_prompt.subprocess.run')
    def test_clone_repository_success(self, mock_run):
        """Test successful repository cloning."""
        from pathlib import Path
        import tempfile

        mock_run.return_value = Mock(returncode=0)
        target_dir = Path(tempfile.mkdtemp())

        result = cmd_prompt.clone_repository("https://github.com/test/repo.git", target_dir)

        assert result is True
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "git" in call_args
        assert "clone" in call_args

    @patch('uzi.cmd_prompt.subprocess.run')
    def test_clone_repository_failure(self, mock_run):
        """Test failed repository cloning."""
        from pathlib import Path
        import tempfile

        mock_run.return_value = Mock(returncode=1)
        target_dir = Path(tempfile.mkdtemp())

        result = cmd_prompt.clone_repository("https://github.com/test/repo.git", target_dir)

        assert result is False


class TestCopyDirectory:
    """Test directory copying functionality."""

    def test_copy_directory_recursive_success(self, temp_dir):
        """Test successful directory copying."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "file.txt").write_text("content")
        (source / "subdir").mkdir()
        (source / "subdir" / "nested.txt").write_text("nested")

        dest = temp_dir / "dest"

        result = cmd_prompt.copy_directory_recursive(source, dest)

        assert result is True
        assert dest.exists()
        assert (dest / "file.txt").read_text() == "content"
        assert (dest / "subdir" / "nested.txt").read_text() == "nested"

    def test_copy_directory_excludes_git(self, temp_dir):
        """Test that .git directory is excluded from copy."""
        source = temp_dir / "source"
        source.mkdir()
        (source / "file.txt").write_text("content")
        git_dir = source / ".git"
        git_dir.mkdir()
        (git_dir / "config").write_text("git config")

        dest = temp_dir / "dest"

        result = cmd_prompt.copy_directory_recursive(source, dest)

        assert result is True
        assert (dest / "file.txt").exists()
        assert not (dest / ".git").exists()

    def test_copy_directory_nonexistent_source(self, temp_dir):
        """Test copying from non-existent source fails gracefully."""
        source = temp_dir / "nonexistent"
        dest = temp_dir / "dest"

        result = cmd_prompt.copy_directory_recursive(source, dest)

        assert result is False


class TestExecutePromptWithOptions:
    """Test execute_prompt with new options."""

    @patch('uzi.cmd_prompt.subprocess.run')
    @patch('uzi.cmd_prompt.copy_directory_recursive', return_value=True)
    @patch('uzi.cmd_prompt.get_random_agent', return_value='testbot')
    @patch('uzi.cmd_prompt.StateManager')
    @patch('uzi.cmd_prompt.load_config')
    def test_execute_prompt_no_worktree(self, mock_load_config, mock_state_manager,
                                        mock_random, mock_copy, mock_run):
        """Test prompt execution with --no-worktree flag."""
        from uzi.config import Config

        mock_load_config.return_value = Config()
        mock_run.return_value = Mock(stdout="output\n", returncode=0)

        mock_sm_instance = Mock()
        mock_state_manager.return_value = mock_sm_instance

        # Execute with no-worktree
        cmd_prompt.execute_prompt("Test prompt", "claude:1", no_worktree=True)

        # Verify copy was called instead of git worktree
        mock_copy.assert_called()

    @patch('uzi.cmd_prompt.subprocess.run')
    @patch('uzi.cmd_prompt.clone_repository', return_value=True)
    @patch('uzi.cmd_prompt.get_random_agent', return_value='testbot')
    @patch('uzi.cmd_prompt.StateManager')
    @patch('uzi.cmd_prompt.load_config')
    @patch('uzi.cmd_prompt.os.chdir')
    def test_execute_prompt_with_clone(self, mock_chdir, mock_load_config, mock_state_manager,
                                       mock_random, mock_clone, mock_run):
        """Test prompt execution with --clone flag."""
        from uzi.config import Config

        mock_load_config.return_value = Config()
        mock_run.return_value = Mock(stdout="abc123\n", returncode=0)

        mock_sm_instance = Mock()
        mock_state_manager.return_value = mock_sm_instance

        # Execute with clone URL
        cmd_prompt.execute_prompt(
            "Test prompt",
            "claude:1",
            clone_url="https://github.com/test/repo.git"
        )

        # Verify clone was called
        mock_clone.assert_called_once()
