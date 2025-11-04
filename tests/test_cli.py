"""Tests for CLI interface."""

from unittest.mock import patch

import pytest

from aimux import cli


class TestCommandAliases:
    """Test command alias resolution."""

    def test_resolve_alias_prompt_full(self):
        """Test resolving full 'prompt' command."""
        result = cli.resolve_alias("prompt")
        assert result == "prompt"

    def test_resolve_alias_prompt_short(self):
        """Test resolving 'p' alias."""
        result = cli.resolve_alias("p")
        assert result == "prompt"

    def test_resolve_alias_ls(self):
        """Test resolving 'ls' and 'l' aliases."""
        assert cli.resolve_alias("ls") == "ls"
        assert cli.resolve_alias("l") == "ls"

    def test_resolve_alias_kill(self):
        """Test resolving 'kill' and 'k' aliases."""
        assert cli.resolve_alias("kill") == "kill"
        assert cli.resolve_alias("k") == "kill"

    def test_resolve_alias_auto(self):
        """Test resolving 'auto' and 'a' aliases."""
        assert cli.resolve_alias("auto") == "auto"
        assert cli.resolve_alias("a") == "auto"

    def test_resolve_alias_broadcast(self):
        """Test resolving 'broadcast' and 'b' aliases."""
        assert cli.resolve_alias("broadcast") == "broadcast"
        assert cli.resolve_alias("b") == "broadcast"

    def test_resolve_alias_checkpoint(self):
        """Test resolving 'checkpoint' and 'c' aliases."""
        assert cli.resolve_alias("checkpoint") == "checkpoint"
        assert cli.resolve_alias("c") == "checkpoint"

    def test_resolve_alias_run(self):
        """Test resolving 'run' and 'r' aliases."""
        assert cli.resolve_alias("run") == "run"
        assert cli.resolve_alias("r") == "run"

    def test_resolve_alias_invalid(self):
        """Test resolving invalid command returns same."""
        result = cli.resolve_alias("invalid")
        assert result == "invalid"

    def test_resolve_alias_partial_matches(self):
        """Test partial matches work correctly."""
        assert cli.resolve_alias("pro") == "prompt"
        # Note: "prompt" regex is ^p(ro(mpt)?)?$ which only matches p, pro, prompt
        # "prom" doesn't match, so it returns itself
        assert cli.resolve_alias("prom") == "prom"


class TestCLIMain:
    """Test main CLI function."""

    @patch("aimux.cli.prompt.execute_prompt")
    def test_main_prompt_command(self, mock_execute):
        """Test main with prompt command."""
        with patch("sys.argv", ["aimux", "prompt", "test prompt"]):
            cli.main()
            mock_execute.assert_called_once()

    @patch("aimux.cli.ls.execute_ls")
    def test_main_ls_command(self, mock_execute):
        """Test main with ls command."""
        with patch("sys.argv", ["aimux", "ls"]):
            cli.main()
            mock_execute.assert_called_once_with(watch=False)

    @patch("aimux.cli.kill.execute_kill")
    def test_main_kill_command(self, mock_execute):
        """Test main with kill command."""
        with patch("sys.argv", ["aimux", "kill", "test-agent"]):
            cli.main()
            mock_execute.assert_called_once_with("test-agent")

    @patch("aimux.cli.auto.execute_auto")
    def test_main_auto_command(self, mock_execute):
        """Test main with auto command."""
        with patch("sys.argv", ["aimux", "auto"]):
            cli.main()
            mock_execute.assert_called_once()

    @patch("aimux.cli.broadcast.execute_broadcast")
    def test_main_broadcast_command(self, mock_execute):
        """Test main with broadcast command."""
        with patch("sys.argv", ["aimux", "broadcast", "test", "message"]):
            cli.main()
            mock_execute.assert_called_once_with("test message")

    @patch("aimux.cli.checkpoint.execute_checkpoint")
    def test_main_checkpoint_command(self, mock_execute):
        """Test main with checkpoint command."""
        with patch("sys.argv", ["aimux", "checkpoint", "agent", "commit message"]):
            cli.main()
            mock_execute.assert_called_once_with("agent", "commit message")

    @patch("aimux.cli.run.execute_run")
    def test_main_run_command(self, mock_execute):
        """Test main with run command."""
        with patch("sys.argv", ["aimux", "run", "git", "status"]):
            cli.main()
            mock_execute.assert_called_once_with("git status", delete=False)

    @patch("aimux.cli.reset.execute_reset")
    def test_main_reset_command(self, mock_execute):
        """Test main with reset command."""
        with patch("sys.argv", ["aimux", "reset"]):
            cli.main()
            mock_execute.assert_called_once()

    def test_main_no_command(self):
        """Test main with no command exits."""
        with patch("sys.argv", ["aimux"]):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 1

    @patch("aimux.cli.ls.execute_ls", side_effect=Exception("Test error"))
    def test_main_command_error(self, mock_execute):
        """Test main handles command errors."""
        with patch("sys.argv", ["aimux", "ls"]):
            with pytest.raises(SystemExit) as exc_info:
                cli.main()
            assert exc_info.value.code == 1

    @patch("aimux.cli.prompt.execute_prompt")
    def test_main_with_alias(self, mock_execute):
        """Test main works with command aliases."""
        with patch("sys.argv", ["aimux", "p", "test"]):
            cli.main()
            mock_execute.assert_called_once()
