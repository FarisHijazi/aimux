"""Checkpoint command - merges agent changes into main branch."""

import os
import subprocess

from ..state import StateManager


def execute_checkpoint(agent_name: str, commit_message: str):
    """Execute the checkpoint command."""
    if not agent_name or not commit_message:
        raise ValueError("Agent name and commit message are required")

    sm = StateManager()
    active_sessions = sm.get_active_sessions_for_repo()

    # Find session with matching agent name
    session_to_checkpoint = None
    for session in active_sessions:
        parts = session.split("-")
        if len(parts) >= 4 and parts[0] == "agent":
            session_agent_name = "-".join(parts[3:])
            if session_agent_name == agent_name:
                session_to_checkpoint = session
                break

    if not session_to_checkpoint:
        raise ValueError(f"No active session found for agent: {agent_name}")

    # Get session state
    states = sm.get_all_states()
    session_state = states.get(session_to_checkpoint)

    if not session_state or not session_state.worktree_path:
        raise ValueError(f"Invalid state for session: {session_to_checkpoint}")

    agent_branch_name = session_state.branch_name

    # Get current directory
    current_dir = os.getcwd()

    # Get current branch
    result = subprocess.run(
        ["git", "branch", "--show-current"],
        cwd=current_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error getting current branch: {result.stderr}")
    current_branch = result.stdout.strip()

    # Check if agent branch exists
    result = subprocess.run(
        ["git", "show-ref", "--verify", "--quiet", f"refs/heads/{agent_branch_name}"],
        cwd=current_dir,
        check=False,
    )
    if result.returncode != 0:
        raise ValueError(f"Agent branch does not exist: {agent_branch_name}")

    # Stage and commit changes on agent branch
    subprocess.run(["git", "add", "."], cwd=session_state.worktree_path, check=False)

    result = subprocess.run(
        ["git", "commit", "-am", commit_message],
        cwd=session_state.worktree_path,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        print("No unstaged changes to commit, rebasing")

    # Get merge base
    result = subprocess.run(
        ["git", "merge-base", current_branch, agent_branch_name],
        cwd=current_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error finding merge base: {result.stderr}")
    merge_base = result.stdout.strip()

    # Check for changes
    result = subprocess.run(
        ["git", "rev-list", "--count", f"{merge_base}..{agent_branch_name}"],
        cwd=current_dir,
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        raise RuntimeError(f"Error checking for changes: {result.stderr}")
    change_count = result.stdout.strip()

    print(f"Checkpointing {change_count} commits from agent: {agent_name}")

    # Rebase agent branch onto current branch
    result = subprocess.run(
        ["git", "rebase", agent_branch_name], cwd=current_dir, check=False
    )
    if result.returncode != 0:
        raise RuntimeError("Error rebasing agent changes")

    print(f"Successfully checkpointed changes from agent: {agent_name}")
    print(f"Successfully committed changes with message: {commit_message}")
