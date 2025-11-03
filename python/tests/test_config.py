"""Tests for configuration management."""

import pytest
from pathlib import Path
from uzi import config


class TestConfig:
    """Test configuration loading functionality."""

    def test_get_default_config_path(self):
        """Test that default config path is returned."""
        path = config.get_default_config_path()
        assert path == "uzi.yaml"

    def test_load_config_nonexistent_file(self):
        """Test loading config from non-existent file returns empty config."""
        cfg = config.load_config("nonexistent_file.yaml")
        assert isinstance(cfg, config.Config)
        assert cfg.dev_command is None
        assert cfg.port_range is None

    def test_load_config_valid_file(self, mock_config_file):
        """Test loading config from valid file."""
        cfg = config.load_config(str(mock_config_file))
        assert isinstance(cfg, config.Config)
        assert cfg.dev_command == "npm run dev -- --port $PORT"
        assert cfg.port_range == "3000-3010"

    def test_config_dataclass_structure(self):
        """Test Config dataclass has correct structure."""
        cfg = config.Config()
        assert hasattr(cfg, 'dev_command')
        assert hasattr(cfg, 'port_range')

    def test_config_with_partial_data(self, temp_dir):
        """Test config with only some fields populated."""
        config_path = temp_dir / "partial.yaml"
        config_path.write_text("devCommand: test command\n")

        cfg = config.load_config(str(config_path))
        assert cfg.dev_command == "test command"
        assert cfg.port_range is None

    def test_config_with_empty_file(self, temp_dir):
        """Test config with empty YAML file."""
        config_path = temp_dir / "empty.yaml"
        config_path.write_text("")

        cfg = config.load_config(str(config_path))
        assert cfg.dev_command is None
        assert cfg.port_range is None

    def test_config_port_range_formats(self, temp_dir):
        """Test various port range formats."""
        config_path = temp_dir / "ports.yaml"

        # Test standard range
        config_path.write_text("portRange: 3000-3010\n")
        cfg = config.load_config(str(config_path))
        assert cfg.port_range == "3000-3010"

        # Test different range
        config_path.write_text("portRange: 8000-9000\n")
        cfg = config.load_config(str(config_path))
        assert cfg.port_range == "8000-9000"

    def test_config_dev_command_with_port_variable(self, temp_dir):
        """Test dev command with $PORT variable."""
        config_path = temp_dir / "dev.yaml"
        config_path.write_text("devCommand: python manage.py runserver 0.0.0.0:$PORT\n")

        cfg = config.load_config(str(config_path))
        assert "$PORT" in cfg.dev_command
