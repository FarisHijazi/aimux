"""Broadcast command - sends a message to all agents."""

import subprocess

from .state import StateManager


def execute_broadcast(message: str):
    """Execute the broadcast command."""
    if not message:
        raise ValueError("Message argument is required")

    sm = StateManager()
    active_sessions = sm.get_active_sessions_for_repo()

    if not active_sessions:
        raise ValueError("No active agent sessions found")

    print(f"Broadcasting message to {len(active_sessions)} agent sessions:")

    for session in active_sessions:
        print(f"\n=== {session} ===")

        # Send message to agent window
        subprocess.run(
            ["tmux", "send-keys", "-t", f"{session}:agent", message, "Enter"],
            capture_output=True,
            check=False
        )
