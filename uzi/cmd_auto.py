"""Auto command - automatically handles agent prompts."""

import hashlib
import signal
import subprocess
import sys
import threading
import time
from typing import Dict, Optional, Set

from .state import StateManager


class SessionMonitor:
    """Monitor for a single session."""

    def __init__(self, session_name: str):
        self.session_name = session_name
        self.prev_output_hash: Optional[bytes] = None
        self.update_count = 0
        self.no_update_count = 0


class AgentWatcher:
    """Watches and manages agent sessions."""

    def __init__(self):
        self.state_manager = StateManager()
        self.watched_sessions: Dict[str, SessionMonitor] = {}
        self.session_threads: Dict[str, threading.Thread] = {}
        self.running = True
        self.lock = threading.Lock()

    def hash_content(self, content: bytes) -> bytes:
        """Hash content for comparison."""
        return hashlib.sha256(content).digest()

    def capture_pane_content(self, session_name: str) -> Optional[str]:
        """Capture tmux pane content."""
        result = subprocess.run(
            ["tmux", "capture-pane", "-t", f"{session_name}:agent", "-p"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode != 0:
            return None
        return result.stdout

    def send_keys(self, session_name: str, keys: str) -> bool:
        """Send keys to a tmux session."""
        result = subprocess.run(
            ["tmux", "send-keys", "-t", f"{session_name}:agent", keys],
            capture_output=True,
            check=False
        )
        return result.returncode == 0

    def tap_enter(self, session_name: str) -> bool:
        """Send Enter key to session."""
        return self.send_keys(session_name, "Enter")

    def has_updated(self, session_name: str) -> tuple:
        """Check if session has updated and if it has a prompt."""
        content = self.capture_pane_content(session_name)
        if content is None:
            return False, False

        # Check for specific prompts
        has_prompt = False

        # Check for Claude trust prompt
        if "Do you trust the files in this folder?" in content:
            has_prompt = True

        # Check for general continuation prompts
        if any(phrase in content for phrase in [
            "Press Enter to continue",
            "Continue? (Y/n)",
            "Do you want to proceed?",
            "Do you want to",
            "Proceed? (y/N)"
        ]):
            has_prompt = True

        # Special case: Allow command but not while Thinking
        if "Allow command" in content and "Thinking" not in content:
            has_prompt = True

        # Check if content has changed
        with self.lock:
            monitor = self.watched_sessions.get(session_name)
            if not monitor:
                # First time monitoring
                self.watched_sessions[session_name] = SessionMonitor(session_name)
                self.watched_sessions[session_name].prev_output_hash = self.hash_content(content.encode())
                return False, has_prompt

            current_hash = self.hash_content(content.encode())
            if current_hash != monitor.prev_output_hash:
                monitor.prev_output_hash = current_hash
                monitor.update_count += 1
                monitor.no_update_count = 0
                return True, has_prompt

            monitor.no_update_count += 1
            return False, has_prompt

    def watch_session(self, session_name: str) -> None:
        """Watch a single session."""
        while self.running:
            try:
                updated, has_prompt = self.has_updated(session_name)

                if has_prompt:
                    print(f"Auto-pressing Enter for prompt in {session_name}")
                    if self.tap_enter(session_name):
                        print(f"Successfully sent Enter to {session_name}")
                    else:
                        print(f"Failed to send Enter to {session_name}")

                time.sleep(0.5)
            except Exception as e:
                print(f"Error watching session {session_name}: {e}")
                time.sleep(2)

    def refresh_active_sessions(self) -> None:
        """Refresh the list of active sessions."""
        try:
            active_sessions = self.state_manager.get_active_sessions_for_repo()

            with self.lock:
                # Remove sessions that are no longer active
                for session_name in list(self.watched_sessions.keys()):
                    if session_name not in active_sessions:
                        print(f"Session {session_name} no longer active, stopping watch")
                        del self.watched_sessions[session_name]
                        # Thread will exit when it checks self.running or notices session is gone

                # Start watching new sessions with dedicated threads
                for session_name in active_sessions:
                    if session_name not in self.watched_sessions:
                        self.watched_sessions[session_name] = SessionMonitor(session_name)
                        thread = threading.Thread(target=self.watch_session, args=(session_name,), daemon=True)
                        self.session_threads[session_name] = thread
                        thread.start()
                        print(f"Started watching session: {session_name}")
        except Exception as e:
            print(f"Error refreshing sessions: {e}")

    def start(self) -> None:
        """Start the agent watcher."""
        print("Starting Agent Watcher")

        # Set up signal handler
        def signal_handler(sig, frame):
            print("\nShutting down Agent Watcher")
            self.running = False
            sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

        # Initial refresh
        self.refresh_active_sessions()

        last_refresh = time.time()
        try:
            while self.running:
                # Refresh sessions every 5 seconds
                if time.time() - last_refresh > 5:
                    self.refresh_active_sessions()
                    last_refresh = time.time()

                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down Agent Watcher")
            self.running = False


def execute_auto():
    """Execute the auto command."""
    watcher = AgentWatcher()
    watcher.start()
