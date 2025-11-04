"""Configuration management for uzi.yaml."""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class Config:
    """Uzi configuration."""
    dev_command: Optional[str] = None
    port_range: Optional[str] = None


def get_default_config_path() -> str:
    """Return the default path for the config file."""
    return "uzi.yaml"


def load_config(path: str) -> Config:
    """Load configuration from the specified path."""
    config_path = Path(path)
    if not config_path.exists():
        return Config()

    with open(config_path, 'r') as f:
        data = yaml.safe_load(f) or {}

    return Config(
        dev_command=data.get('devCommand'),
        port_range=data.get('portRange')
    )
