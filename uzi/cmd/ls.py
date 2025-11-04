"""List command - shows active agent sessions."""

import re
import subprocess
import time
from datetime import datetime

from ..state import StateManager


def get_git_diff_totals(session_name: str, state_manager: StateManager) -> tuple:
    """Get git diff statistics for a session."""
    states = state_manager.get_all_states()
    session_state = states.get(session_name)

    if not session_state or not session_state.worktree_path:
        return 0, 0

    shell_cmd = "git add -A . && git diff --cached --shortstat HEAD && git reset HEAD > /dev/null 2>&1"
    result = subprocess.run(
        shell_cmd,
        shell=True,
        cwd=session_state.worktree_path,
        capture_output=True,
        text=True,
        check=False,
    )

    if result.returncode != 0:
        return 0, 0

    output = result.stdout
    insertions = 0
    deletions = 0

    ins_match = re.search(r"(\d+) insertion(?:s)?\(\+\)", output)
    del_match = re.search(r"(\d+) deletion(?:s)?\(\-\)", output)

    if ins_match:
        insertions = int(ins_match.group(1))
    if del_match:
        deletions = int(del_match.group(1))

    return insertions, deletions


def get_pane_content(session_name: str) -> str:
    """Get tmux pane content."""
    result = subprocess.run(
        ["tmux", "capture-pane", "-t", f"{session_name}:agent", "-p"],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        return ""
    return result.stdout


def get_agent_status(session_name: str) -> str:
    """Get the current status of an agent."""
    content = get_pane_content(session_name)
    if not content:
        return "unknown"

    if "esc to interrupt" in content or "Thinking" in content:
        return "running"
    return "ready"


def format_status(status: str) -> str:
    """Format status with color codes."""
    if status == "ready":
        return "\033[32mready\033[0m"  # Green
    elif status == "running":
        return "\033[33mrunning\033[0m"  # Yellow
    return status


def print_sessions(state_manager: StateManager, active_sessions: list) -> None:
    """Print session information in a formatted table."""
    if not active_sessions:
        print("No active sessions found")
        return

    states = state_manager.get_all_states()

    # Sort by updated_at (most recent first)
    sessions = []
    for session_name in active_sessions:
        if session_name in states:
            sessions.append((session_name, states[session_name]))

    sessions.sort(key=lambda x: x[1].updated_at, reverse=True)

    # Print header
    print(
        f"{'AGENT':<15} {'MODEL':<10} {'STATUS':<20} {'DIFF':<15} {'ADDR':<30} PROMPT"
    )

    # Print sessions
    for session_name, state in sessions:
        # Extract agent name from session name
        parts = session_name.split("-")
        agent_name = session_name
        if len(parts) >= 4 and parts[0] == "agent":
            agent_name = "-".join(parts[3:])

        status = get_agent_status(session_name)
        insertions, deletions = get_git_diff_totals(session_name, state_manager)

        # Format diff stats with colors
        if insertions == 0 and deletions == 0:
            changes = "\033[32m+0\033[0m/\033[31m-0\033[0m"
        else:
            changes = f"\033[32m+{insertions}\033[0m/\033[31m-{deletions}\033[0m"

        model = state.model if state.model else "unknown"

        addr = ""
        if state.port:
            addr = f"http://localhost:{state.port}"

        # Truncate prompt if too long
        prompt = state.prompt
        if len(prompt) > 50:
            prompt = prompt[:47] + "..."

        print(
            f"{agent_name:<15} {model:<10} {format_status(status):<20} {changes:<25} {addr:<30} {prompt}"
        )


def execute_ls(watch: bool = False):
    """Execute the ls command."""
    state_manager = StateManager()

    if watch:
        # Watch mode - refresh every second
        try:
            while True:
                # Clear screen
                print("\033[H\033[2J", end="")

                active_sessions = state_manager.get_active_sessions_for_repo()
                print_sessions(state_manager, active_sessions)

                time.sleep(1)
        except KeyboardInterrupt:
            print("\nExiting watch mode")
    else:
        # Single run mode
        active_sessions = state_manager.get_active_sessions_for_repo()
        print_sessions(state_manager, active_sessions)
