"""Kill command - terminates agent sessions."""

import shutil
import subprocess
from pathlib import Path

from ..state import StateManager


def kill_session(session_name: str, agent_name: str, sm: StateManager) -> None:
    """Kill a single session and clean up resources."""
    print(f"Deleting tmux session and git worktree for {session_name}")

    # Kill tmux session if it exists
    result = subprocess.run(
        ["tmux", "has-session", "-t", session_name], capture_output=True, check=False
    )
    if result.returncode == 0:
        subprocess.run(
            ["tmux", "kill-session", "-t", session_name],
            capture_output=True,
            check=False,
        )

    # Get worktree info
    worktree_info = sm.get_worktree_info(session_name)
    if worktree_info:
        # Remove worktree
        subprocess.run(
            ["git", "worktree", "remove", "--force", worktree_info.worktree_path],
            capture_output=True,
            check=False,
        )

        # Delete branch
        subprocess.run(
            ["git", "branch", "-D", worktree_info.branch_name],
            capture_output=True,
            check=False,
        )

    # Delete from config store
    home_dir = Path.home()

    # Remove worktree directory from config store
    config_worktree_path = home_dir / ".local" / "share" / "uzi" / "worktrees"
    if config_worktree_path.exists():
        for item in config_worktree_path.iterdir():
            if agent_name in item.name:
                shutil.rmtree(item, ignore_errors=True)

    # Remove worktree state directory
    worktree_state_path = (
        home_dir / ".local" / "share" / "uzi" / "worktree" / session_name
    )
    if worktree_state_path.exists():
        shutil.rmtree(worktree_state_path, ignore_errors=True)

    # Remove from state.json
    sm.remove_state(session_name)


def kill_all(sm: StateManager) -> None:
    """Kill all sessions for the current repository."""
    print("Deleting all agents for repository")

    active_sessions = sm.get_active_sessions_for_repo()

    if not active_sessions:
        print("No active sessions found")
        return

    killed_count = 0
    for session_name in active_sessions:
        parts = session_name.split("-")
        if len(parts) >= 2:
            agent_name = "-".join(parts[3:]) if parts[0] == "agent" else parts[-1]
            kill_session(session_name, agent_name, sm)
            killed_count += 1
            print(f"Deleted agent: {agent_name}")

    print(f"Successfully deleted {killed_count} agent(s)")


def execute_kill(agent_name: str):
    """Execute the kill command."""
    if not agent_name:
        raise ValueError("Agent name argument is required")

    sm = StateManager()

    if agent_name == "all":
        kill_all(sm)
        return

    # Find the session with matching agent name
    active_sessions = sm.get_active_sessions_for_repo()
    session_to_kill = None

    for session in active_sessions:
        if session.endswith(f"-{agent_name}"):
            session_to_kill = session
            break

    if not session_to_kill:
        raise ValueError(f"No active session found for agent: {agent_name}")

    kill_session(session_to_kill, agent_name, sm)
    print(f"Deleted agent: {agent_name}")
