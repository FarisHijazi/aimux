"""State management for tracking agent sessions."""

import json
import os
import shutil
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


@dataclass
class AgentState:
    """State for a single agent session."""

    git_repo: str
    branch_from: str
    branch_name: str
    prompt: str
    worktree_path: str
    model: str
    created_at: str
    updated_at: str
    port: int = 0


class StateManager:
    """Manages persistent state for agent sessions."""

    def __init__(self):
        """Initialize state manager."""
        home_dir = Path.home()
        self.state_path = home_dir / ".local" / "share" / "uzi" / "state.json"

    def _ensure_state_dir(self) -> None:
        """Ensure the state directory exists."""
        self.state_path.parent.mkdir(parents=True, exist_ok=True)

    def _get_git_repo(self) -> str:
        """Get the current git repository URL."""
        try:
            result = subprocess.run(
                ["git", "config", "--get", "remote.origin.url"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _get_branch_from(self) -> str:
        """Get the main/master branch name."""
        try:
            result = subprocess.run(
                ["git", "symbolic-ref", "refs/remotes/origin/HEAD"],
                capture_output=True,
                text=True,
                check=False,
            )
            if result.returncode == 0:
                ref = result.stdout.strip()
                parts = ref.split("/")
                if parts:
                    return parts[-1]
        except Exception:
            pass
        return "main"

    def _is_active_in_tmux(self, session_name: str) -> bool:
        """Check if a tmux session is active."""
        result = subprocess.run(
            ["tmux", "has-session", "-t", session_name],
            capture_output=True,
            check=False,
        )
        return result.returncode == 0

    def get_active_sessions_for_repo(self) -> List[str]:
        """Get all active sessions for the current repository."""
        if not self.state_path.exists():
            return []

        with open(self.state_path, "r") as f:
            states: Dict[str, dict] = json.load(f)

        current_repo = self._get_git_repo()
        if not current_repo:
            return []

        active_sessions = []
        for session_name, state in states.items():
            if state.get("git_repo") == current_repo and self._is_active_in_tmux(
                session_name
            ):
                active_sessions.append(session_name)

        return active_sessions

    def save_state(
        self,
        prompt: str,
        branch_name: str,
        session_name: str,
        worktree_path: str,
        model: str,
        port: int = 0,
    ) -> None:
        """Save agent state to disk."""
        self._ensure_state_dir()

        # Load existing state with error recovery
        states: Dict[str, dict] = {}
        if self.state_path.exists():
            try:
                with open(self.state_path, "r") as f:
                    states = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                # Backup corrupted file
                backup_path = self.state_path.with_suffix(".json.backup")
                try:
                    shutil.copy(self.state_path, backup_path)
                    print(
                        f"Warning: Corrupted state file backed up to {backup_path}",
                        file=sys.stderr,
                    )
                except Exception:
                    pass
                states = {}

        # Create new state entry
        now = datetime.now().isoformat()
        agent_state = AgentState(
            git_repo=self._get_git_repo(),
            branch_from=self._get_branch_from(),
            branch_name=branch_name,
            prompt=prompt,
            worktree_path=worktree_path,
            port=port,
            model=model,
            created_at=states.get(session_name, {}).get("created_at", now),
            updated_at=now,
        )

        states[session_name] = asdict(agent_state)

        # Store worktree branch
        self._store_worktree_branch(session_name)

        # Save to file
        with open(self.state_path, "w") as f:
            json.dump(states, f, indent=2)

    def _get_current_branch(self) -> str:
        """Get the current git branch."""
        try:
            result = subprocess.run(
                ["git", "branch", "--show-current"],
                capture_output=True,
                text=True,
                check=False,
            )
            return result.stdout.strip()
        except Exception:
            return ""

    def _store_worktree_branch(self, session_name: str) -> None:
        """Store the worktree branch for a session."""
        home_dir = Path.home()
        agent_dir = home_dir / ".local" / "share" / "uzi" / "worktree" / session_name
        agent_dir.mkdir(parents=True, exist_ok=True)

        branch_file = agent_dir / "tree"
        current_branch = self._get_current_branch()
        if current_branch:
            branch_file.write_text(current_branch)

    def remove_state(self, session_name: str) -> None:
        """Remove agent state from disk."""
        if not self.state_path.exists():
            return

        with open(self.state_path, "r") as f:
            states: Dict[str, dict] = json.load(f)

        states.pop(session_name, None)

        with open(self.state_path, "w") as f:
            json.dump(states, f, indent=2)

    def get_worktree_info(self, session_name: str) -> Optional[AgentState]:
        """Get worktree information for a session."""
        if not self.state_path.exists():
            return None

        with open(self.state_path, "r") as f:
            states: Dict[str, dict] = json.load(f)

        state_dict = states.get(session_name)
        if not state_dict:
            return None

        return AgentState(**state_dict)

    def get_all_states(self) -> Dict[str, AgentState]:
        """Get all agent states."""
        if not self.state_path.exists():
            return {}

        try:
            with open(self.state_path, "r") as f:
                states: Dict[str, dict] = json.load(f)

            return {name: AgentState(**state) for name, state in states.items()}
        except (json.JSONDecodeError, IOError) as e:
            print(f"Error reading state file: {e}", file=sys.stderr)
            return {}
