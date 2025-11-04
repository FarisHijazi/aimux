"""Run command - executes a command in all agent sessions."""

import subprocess

from .state import StateManager


def execute_run(command: str, delete: bool = False):
    """Execute the run command."""
    if not command:
        raise ValueError("No command provided")

    sm = StateManager()
    active_sessions = sm.get_active_sessions_for_repo()

    if not active_sessions:
        raise ValueError("No active agent sessions found")

    print(f"Running command '{command}' in {len(active_sessions)} agent sessions:")

    for session in active_sessions:
        print(f"\n=== {session} ===")

        # Create new window
        result = subprocess.run(
            ["tmux", "new-window", "-t", session, "-P", "-F", "#{window_index}", "-c", "#{session_path}"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode != 0:
            print(f"Failed to create new window: {result.stderr}")
            continue

        window_index = result.stdout.strip()
        window_target = f"{session}:{window_index}"

        # Send command
        result = subprocess.run(
            ["tmux", "send-keys", "-t", window_target, command, "Enter"],
            capture_output=True,
            check=False
        )

        if result.returncode != 0:
            print(f"Failed to send command: {result.stderr}")
            continue

        # Capture output
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", window_target, "-p"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            output = result.stdout.strip()
            if output:
                print(output)

        # Delete window if requested
        if delete:
            subprocess.run(
                ["tmux", "kill-window", "-t", window_target],
                capture_output=True,
                check=False
            )
