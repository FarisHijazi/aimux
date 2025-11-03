# Uzi - Python Implementation

A Python implementation of Uzi, an AI coding agent orchestration tool.

## Installation

```bash
cd python
pip install -e .
```

## Prerequisites

- Python 3.11+
- Git (for version control and worktree management)
- Tmux (for terminal session management)
- Your AI tool of choice (such as `claude`, `codex`, etc.)

## Configuration

Create a `uzi.yaml` file in your project root:

```yaml
devCommand: cd myproject && npm install && npm run dev -- --port $PORT
portRange: 3000-3010
```

## Basic Usage

```bash
# Create agent sessions
uzi prompt --agents claude:2 "Implement a REST API"

# List active sessions
uzi ls

# Watch sessions
uzi ls -w

# Send message to all agents
uzi broadcast "Add error handling"

# Auto-handle prompts
uzi auto

# Kill agent
uzi kill agent-name

# Kill all agents
uzi kill all

# Checkpoint changes
uzi checkpoint agent-name "feat: add API"

# Run command in all sessions
uzi run "git status"

# Reset all data
uzi reset
```

## Command Aliases

- `uzi p` - prompt
- `uzi l` - ls
- `uzi k` - kill
- `uzi a` - auto
- `uzi b` - broadcast
- `uzi c` - checkpoint
- `uzi r` - run

## License

BSD-3-Clause
