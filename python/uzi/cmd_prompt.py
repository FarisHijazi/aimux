"""Prompt command - creates new agent sessions."""

import os
import socket
import subprocess
import time
from pathlib import Path
from typing import Dict, List

from .agents import get_random_agent
from .config import Config, get_default_config_path, load_config
from .state import StateManager


def is_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", port))
            return True
    except OSError:
        return False


def find_available_port(start_port: int, end_port: int, assigned_ports: List[int]) -> int:
    """Find the first available port in the given range."""
    for port in range(start_port, end_port + 1):
        if port in assigned_ports:
            continue
        if is_port_available(port):
            return port
    raise RuntimeError(f"No available ports in range {start_port}-{end_port}")


def parse_agents(agents_str: str) -> Dict[str, Dict[str, any]]:
    """Parse agent specification string like 'claude:2,codex:1'."""
    agent_configs = {}

    for pair in agents_str.split(','):
        parts = pair.strip().split(':')
        if len(parts) != 2:
            raise ValueError(f"Invalid agent format: {pair} (expected agent:count)")

        agent = parts[0].strip()
        try:
            count = int(parts[1].strip())
        except ValueError:
            raise ValueError(f"Invalid count for agent {agent}: {parts[1]}")

        if count < 1:
            raise ValueError(f"Count must be at least 1 for agent {agent}")

        agent_configs[agent] = {"command": agent, "count": count}

    return agent_configs


def execute_prompt(prompt_text: str, agents_str: str = "claude:1", config_path: str = None):
    """Execute the prompt command."""
    if not prompt_text:
        raise ValueError("Prompt argument is required")

    # Load config
    if config_path is None:
        config_path = get_default_config_path()

    try:
        cfg = load_config(config_path)
    except Exception:
        cfg = Config()

    if not cfg.dev_command:
        print("Dev command not set in config, skipping dev server startup.")
    if not cfg.port_range:
        print("Port range not set in config, skipping dev server startup.")

    assigned_ports = []
    agent_configs = parse_agents(agents_str)
    state_manager = StateManager()

    for agent, config in agent_configs.items():
        for i in range(config["count"]):
            # Get random agent name
            random_agent_name = get_random_agent()

            # Use specified agent for command (unless it's "random")
            command_to_use = config["command"]
            if agent == "random":
                command_to_use = random_agent_name

            print(f"{random_agent_name}: {command_to_use}: {prompt_text}")

            # Get git hash
            result = subprocess.run(
                ["git", "rev-parse", "--short", "HEAD"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print(f"Error getting git hash: {result.stderr}")
                continue
            git_hash = result.stdout.strip()

            # Get repository name
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print(f"Error getting git remote: {result.stderr}")
                continue
            remote_url = result.stdout.strip()
            repo_name = Path(remote_url).stem.replace('.git', '')

            # Create unique identifiers
            timestamp = int(time.time())
            unique_id = f"{timestamp}-{i}"

            # Create branch and worktree names
            branch_name = f"{random_agent_name}-{repo_name}-{git_hash}-{unique_id}"
            worktree_name = f"{random_agent_name}-{repo_name}-{git_hash}-{unique_id}"
            session_name = f"agent-{repo_name}-{git_hash}-{random_agent_name}"

            # Create worktree path
            home_dir = Path.home()
            worktrees_dir = home_dir / ".local" / "share" / "uzi" / "worktrees"
            worktrees_dir.mkdir(parents=True, exist_ok=True)
            worktree_path = worktrees_dir / worktree_name

            # Create git worktree
            result = subprocess.run(
                ["git", "worktree", "add", "-b", branch_name, str(worktree_path)],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print(f"Error creating git worktree: {result.stderr}")
                continue

            # Create tmux session
            result = subprocess.run(
                ["tmux", "new-session", "-d", "-s", session_name, "-c", str(worktree_path)],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print(f"Error creating tmux session: {result.stderr}")
                continue

            # Rename first window to "agent"
            subprocess.run(
                ["tmux", "rename-window", "-t", f"{session_name}:0", "agent"],
                capture_output=True,
                check=False
            )

            selected_port = 0

            # Handle dev command if configured
            if cfg.dev_command and cfg.port_range:
                try:
                    ports = cfg.port_range.split('-')
                    if len(ports) == 2:
                        start_port = int(ports[0])
                        end_port = int(ports[1])

                        if 1 <= start_port <= 65535 and 1 <= end_port <= 65535 and end_port >= start_port:
                            selected_port = find_available_port(start_port, end_port, assigned_ports)
                            assigned_ports.append(selected_port)

                            dev_cmd = cfg.dev_command.replace("$PORT", str(selected_port))

                            # Create uzi-dev window
                            subprocess.run(
                                ["tmux", "new-window", "-t", session_name, "-n", "uzi-dev", "-c", str(worktree_path)],
                                capture_output=True,
                                check=False
                            )

                            # Send dev command
                            subprocess.run(
                                ["tmux", "send-keys", "-t", f"{session_name}:uzi-dev", dev_cmd, "C-m"],
                                capture_output=True,
                                check=False
                            )
                except Exception as e:
                    print(f"Error setting up dev server: {e}")

            # Hit enter in agent pane
            subprocess.run(
                ["tmux", "send-keys", "-t", f"{session_name}:agent", "C-m"],
                capture_output=True,
                check=False
            )

            # Send the prompt to agent pane
            full_command = f'{command_to_use} "{prompt_text}"'
            result = subprocess.run(
                ["tmux", "send-keys", "-t", f"{session_name}:agent", full_command, "C-m"],
                capture_output=True,
                text=True,
                check=False
            )
            if result.returncode != 0:
                print(f"Error sending keys to tmux: {result.stderr}")
                continue

            # Save state
            state_manager.save_state(
                prompt=prompt_text,
                branch_name=branch_name,
                session_name=session_name,
                worktree_path=str(worktree_path),
                model=command_to_use,
                port=selected_port
            )
