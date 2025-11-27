"""Prompt command - creates new agent sessions."""

import os
import shutil
import socket
import subprocess
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional

from ..agents import get_random_agent
from ..config import Config, get_default_config_path, load_config
from ..state import StateManager


def is_port_available(port: int) -> bool:
    """Check if a port is available."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(("", port))
            return True
    except OSError:
        return False


def find_available_port(
    start_port: int, end_port: int, assigned_ports: List[int]
) -> int:
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

    for pair in agents_str.split(","):
        parts = pair.strip().split(":")
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


def clone_repository(repo_url: str, target_dir: Path) -> bool:
    """Clone a repository from URL to target directory."""
    try:
        result = subprocess.run(
            ["git", "clone", repo_url, str(target_dir)],
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error cloning repository: {e}")
        return False


def copy_directory_recursive(source: Path, destination: Path) -> bool:
    """Recursively copy a directory, excluding git metadata."""
    try:
        # Copy the entire directory
        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns(".git"),
            symlinks=True,
            dirs_exist_ok=False,
        )
        return True
    except Exception as e:
        print(f"Error copying directory: {e}")
        return False


def execute_prompt(
    prompt_text: str,
    agents_str: str = "claude:1",
    config_path: str = None,
    init_method: Optional[str] = None,
    url: Optional[str] = None,
    no_worktree: bool = False,
    clone_url: Optional[str] = None,
):
    """Execute the prompt command.

    Args:
        prompt_text: The prompt to send to agents
        agents_str: Agent specification (e.g., "claude:2,codex:1")
        config_path: Path to config file
        init_method: Initialization method: 'worktree', 'copy', or 'clone'
        url: Repository URL (required when init_method='clone')
        no_worktree: [DEPRECATED] If True, copy directory instead of using git worktrees
        clone_url: [DEPRECATED] If provided, clone from this URL instead of using current repo
    """
    if not prompt_text:
        raise ValueError("Prompt argument is required")

    # Load config first to get default init method
    if config_path is None:
        config_path = get_default_config_path()

    try:
        cfg = load_config(config_path)
    except Exception:
        cfg = Config()

    # Handle backward compatibility and determine actual initialization method
    actual_init_method = init_method
    actual_url = url

    # Legacy flag handling
    if clone_url and not actual_init_method:
        print("Warning: --clone is deprecated. Use --init-method=clone --url=URL instead")
        actual_init_method = "clone"
        actual_url = clone_url
    elif no_worktree and not actual_init_method:
        print("Warning: --no-worktree is deprecated. Use --init-method=copy instead")
        actual_init_method = "copy"

    # Auto-detect clone method if URL is provided without explicit method
    if actual_url and not actual_init_method:
        actual_init_method = "clone"

    # Use config default if not specified
    if not actual_init_method and cfg.default_init_method:
        actual_init_method = cfg.default_init_method
        if actual_init_method not in ["worktree", "copy", "clone"]:
            print(f"Warning: Invalid defaultInitMethod '{actual_init_method}' in config, using 'worktree'")
            actual_init_method = "worktree"

    # Default to worktree if still not specified
    if not actual_init_method:
        actual_init_method = "worktree"

    # Validate clone method has URL
    if actual_init_method == "clone" and not actual_url:
        raise ValueError("--url is required when using --init-method=clone")

    # Show which initialization method is being used
    method_descriptions = {
        "worktree": "git worktrees (linked to current repository)",
        "copy": "hard copy of project directory",
        "clone": f"git clone from {actual_url}",
    }
    print(f"Initialization method: {method_descriptions.get(actual_init_method, actual_init_method)}")

    # Convert to flags for compatibility with existing code
    use_worktree = actual_init_method == "worktree"
    use_clone = actual_init_method == "clone"
    clone_source_url = actual_url if use_clone else None

    # Config is already loaded above
    if not cfg.dev_command:
        print("Dev command not set in config, skipping dev server startup.")
    if not cfg.port_range:
        print("Port range not set in config, skipping dev server startup.")

    assigned_ports = []
    agent_configs = parse_agents(agents_str)
    state_manager = StateManager()

    # Handle cloning from URL if specified
    clone_source_dir = None
    if use_clone:
        print(f"Cloning repository from {clone_source_url}...")
        clone_source_dir = Path(tempfile.mkdtemp(prefix="aimux_clone_"))
        if not clone_repository(clone_source_url, clone_source_dir):
            print(f"Failed to clone repository from {clone_source_url}")
            if clone_source_dir.exists():
                shutil.rmtree(clone_source_dir, ignore_errors=True)
            return
        print(f"Repository cloned to {clone_source_dir}")

        # Change to cloned directory for subsequent operations
        original_dir = os.getcwd()
        os.chdir(clone_source_dir)

    try:
        for agent, config in agent_configs.items():
            for i in range(config["count"]):
                # Get random agent name
                random_agent_name = get_random_agent()

                # Use specified agent for command (unless it's "random")
                command_to_use = config["command"]
                if agent == "random":
                    command_to_use = random_agent_name

                print(f"{random_agent_name}: {command_to_use}: {prompt_text}")

                # Get current directory (either original or cloned)
                current_source = Path(os.getcwd())

                # Get git hash and repo name
                if not use_worktree:
                    # For directory copy mode, use timestamp as identifier
                    git_hash = f"copy-{int(time.time())}"
                    repo_name = current_source.name
                else:
                    # Get git hash
                    result = subprocess.run(
                        ["git", "rev-parse", "--short", "HEAD"],
                        capture_output=True,
                        text=True,
                        check=False,
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
                        check=False,
                    )
                    if result.returncode != 0:
                        print(f"Error getting git remote: {result.stderr}")
                        continue
                    remote_url = result.stdout.strip()
                    repo_name = Path(remote_url).stem.replace(".git", "")

                # Create unique identifiers
                timestamp = int(time.time())
                unique_id = f"{timestamp}-{i}"

                # Create branch and worktree names
                branch_name = f"{random_agent_name}-{repo_name}-{git_hash}-{unique_id}"
                worktree_name = (
                    f"{random_agent_name}-{repo_name}-{git_hash}-{unique_id}"
                )
                session_name = f"agent-{repo_name}-{git_hash}-{random_agent_name}"

                # Create worktree/copy path
                home_dir = Path.home()
                if use_worktree:
                    base_dir = home_dir / ".local" / "share" / "aimux" / "worktrees"
                else:
                    base_dir = home_dir / ".local" / "share" / "aimux" / "copies"
                base_dir.mkdir(parents=True, exist_ok=True)
                worktree_path = base_dir / worktree_name

                # Create git worktree or copy directory
                if use_worktree:
                    print(f"Creating git worktree at {worktree_path}...")
                    result = subprocess.run(
                        [
                            "git",
                            "worktree",
                            "add",
                            "-b",
                            branch_name,
                            str(worktree_path),
                        ],
                        capture_output=True,
                        text=True,
                        check=False,
                    )
                    if result.returncode != 0:
                        print(f"Error creating git worktree: {result.stderr}")
                        continue
                else:
                    print(f"Copying directory to {worktree_path}...")
                    if not copy_directory_recursive(current_source, worktree_path):
                        print(f"Error copying directory")
                        continue
                    # Initialize git in the copy if it doesn't have .git
                    git_dir = worktree_path / ".git"
                    if not git_dir.exists():
                        subprocess.run(
                            ["git", "init"],
                            cwd=str(worktree_path),
                            capture_output=True,
                            check=False,
                        )
                        subprocess.run(
                            ["git", "add", "."],
                            cwd=str(worktree_path),
                            capture_output=True,
                            check=False,
                        )
                        subprocess.run(
                            ["git", "commit", "-m", "Initial copy"],
                            cwd=str(worktree_path),
                            capture_output=True,
                            check=False,
                        )

                # Create tmux session
                result = subprocess.run(
                    [
                        "tmux",
                        "new-session",
                        "-d",
                        "-s",
                        session_name,
                        "-c",
                        str(worktree_path),
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
                )
                if result.returncode != 0:
                    print(f"Error creating tmux session: {result.stderr}")
                    continue

                # Rename first window to "agent"
                subprocess.run(
                    ["tmux", "rename-window", "-t", f"{session_name}:0", "agent"],
                    capture_output=True,
                    check=False,
                )

                selected_port = 0

                # Handle dev command if configured
                if cfg.dev_command and cfg.port_range:
                    try:
                        ports = cfg.port_range.split("-")
                        if len(ports) == 2:
                            start_port = int(ports[0])
                            end_port = int(ports[1])

                            if (
                                1 <= start_port <= 65535
                                and 1 <= end_port <= 65535
                                and end_port >= start_port
                            ):
                                selected_port = find_available_port(
                                    start_port, end_port, assigned_ports
                                )
                                assigned_ports.append(selected_port)

                                dev_cmd = cfg.dev_command.replace(
                                    "$PORT", str(selected_port)
                                )

                                # Create aimux-dev window
                                subprocess.run(
                                    [
                                        "tmux",
                                        "new-window",
                                        "-t",
                                        session_name,
                                        "-n",
                                        "aimux-dev",
                                        "-c",
                                        str(worktree_path),
                                    ],
                                    capture_output=True,
                                    check=False,
                                )

                                # Send dev command
                                subprocess.run(
                                    [
                                        "tmux",
                                        "send-keys",
                                        "-t",
                                        f"{session_name}:aimux-dev",
                                        dev_cmd,
                                        "C-m",
                                    ],
                                    capture_output=True,
                                    check=False,
                                )
                    except Exception as e:
                        print(f"Error setting up dev server: {e}")

                # Hit enter in agent pane
                subprocess.run(
                    ["tmux", "send-keys", "-t", f"{session_name}:agent", "C-m"],
                    capture_output=True,
                    check=False,
                )

                # Send the prompt to agent pane
                full_command = f'{command_to_use} "{prompt_text}"'
                result = subprocess.run(
                    [
                        "tmux",
                        "send-keys",
                        "-t",
                        f"{session_name}:agent",
                        full_command,
                        "C-m",
                    ],
                    capture_output=True,
                    text=True,
                    check=False,
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
                    port=selected_port,
                )
    finally:
        # Cleanup cloned directory and restore original directory
        if use_clone and clone_source_dir:
            os.chdir(original_dir)
            if clone_source_dir.exists():
                shutil.rmtree(clone_source_dir, ignore_errors=True)
