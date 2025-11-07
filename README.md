# aimux - Python Implementation

A Python 3.11+ implementation of aimux, an AI coding agent orchestration tool that helps you manage multiple AI coding agents working on the same codebase in parallel, each in isolated environments with tmux sessions.

## Quick Start

Try it instantly without installation:

```bash
uvx --from git+https://github.com/FarisHijazi/aimux aimux --help
```

## Features

✨ **Core Functionality**
- 🤖 **8 Commands**: prompt, ls, kill, auto, broadcast, checkpoint, run, reset
- 🔄 **Agent Orchestration**: Manage multiple AI agents working concurrently
- 🌳 **Git Worktrees**: Isolated development environments sharing git objects
- 📦 **Directory Copies**: Alternative to worktrees for maximum isolation
- 🔗 **Clone from URLs**: Work with any GitHub/GitLab repo instantly
- 💬 **Tmux Integration**: Each agent in its own terminal session
- 💾 **State Persistence**: Track all agent sessions across restarts
- ⚡ **Command Aliases**: Short forms for faster workflow (p, l, k, a, b, c, r)

🛡️ **Security & Quality**
- ✅ **Shell Injection Prevention**: All subprocess calls use list-based arguments
- 🔒 **Input Validation**: Port ranges, agent names, paths validated
- 💪 **Error Recovery**: Automatic state file corruption handling with backups
- 🧪 **Comprehensive Tests**: 83 pytest tests with 57% overall coverage
- 📊 **100% Coverage**: Core modules (agents, config) fully tested

🚀 **Modern Python Packaging**
- 📦 **uv Support**: Fast, modern dependency management with lock file
- 🎯 **uvx Compatible**: Run without installation
- 🐍 **pip Compatible**: Standard Python packaging with pyproject.toml
- 🔧 **Python 3.11+**: Uses modern Python features

## Installation

### Using uvx (recommended - no installation required)

Run directly from GitHub without cloning or installing:

```bash
# Try it out
uvx --from git+https://github.com/FarisHijazi/aimux aimux --help

# Create an alias for convenience
alias aimux='uvx --from git+https://github.com/FarisHijazi/aimux aimux'
```

### Using uvx (local development)

If you've cloned the repo:

```bash
uvx --from . aimux --help
```

### Using uv (for local development with venv)

```bash
uv sync
# Then either activate: source .venv/bin/activate
# Or prefix commands: uv run aimux --help
```

This creates a virtual environment with pinned dependencies via uv.lock.

### Using pip (development install)

```bash
pip install -e .
```

### Using pip (from PyPI)

```bash
pip install aimux  # Coming soon
```

## Prerequisites

- Python 3.11+
- Git (for version control and worktree management)
- Tmux (for terminal session management)
- Your AI tool of choice (such as `claude`, `codex`, etc.)
- [uv](https://docs.astral.sh/uv/) (optional but recommended for faster dependency management)

## Configuration

Create a `aimux.yaml` file in your project root:

```yaml
devCommand: cd myproject && npm install && npm run dev -- --port $PORT
portRange: 3000-3010
```

## Basic Usage

> **Note:**
> - If using uvx from GitHub: `uvx --from git+https://github.com/FarisHijazi/aimux aimux <command>`
> - If installed with `uv sync`: activate venv or prefix with `uv run aimux <command>`
> - If using uvx locally: `uvx --from . aimux <command>`
> - If installed with pip: just use `aimux <command>`

```bash
# Create agent sessions (uses git worktrees by default)
aimux prompt --agents claude:2 "Implement a REST API"

# Create agent sessions with directory copies instead of worktrees
aimux prompt --init-method=copy --agents claude:2 "Implement a REST API"

# Create agent sessions by cloning from a repository URL
aimux prompt --init-method=clone --url=https://github.com/user/repo.git --agents claude:2 "Implement a REST API"

# Legacy syntax (deprecated but still supported)
aimux prompt --no-worktree --agents claude:2 "Implement a REST API"
aimux prompt --clone https://github.com/user/repo.git --agents claude:2 "Implement a REST API"

# List active sessions
aimux ls

# Watch sessions
aimux ls -w

# Send message to all agents
aimux broadcast "Add error handling"

# Auto-handle prompts
aimux auto

# Kill agent
aimux kill agent-name

# Kill all agents
aimux kill all

# Checkpoint changes
aimux checkpoint agent-name "feat: add API"

# Run command in all sessions
aimux run "git status"

# Reset all data
aimux reset
```

## Advanced Options

### Choosing Project Initialization Method

Aimux supports three methods to initialize project environments for agents. Use the `--init-method` parameter to choose:

#### 1. Git Worktrees (Default)
```bash
aimux prompt --init-method=worktree --agents claude:2 "Your task"
# Or simply omit --init-method (worktree is default)
aimux prompt --agents claude:2 "Your task"
```

**Benefits:**
- Minimal disk space (shares git objects)
- Fast setup
- All changes tracked in git branches
- Easy to merge back to main

**Best for:** Regular git projects where you want proper version control

#### 2. Hard Copy
```bash
aimux prompt --init-method=copy --agents claude:2 "Your task"
```

**Benefits:**
- Works with non-git directories
- Full independence from main repository
- No git worktree limitations
- Easier to understand for beginners

**Tradeoffs:**
- Uses more disk space (full copies)
- Changes aren't automatically tracked with git branches
- Slower initial setup (full copy vs. worktree)

**Best for:** Non-git projects or when you need complete isolation

#### 3. Clone from URL
```bash
aimux prompt --init-method=clone --url=https://github.com/user/repo.git --agents claude:2 "Your task"
```

**Benefits:**
- Work on any GitHub/GitLab repository instantly
- No need to have the repo cloned locally
- Supports both public and private repositories
- Automatic cleanup after agent creation

**Best for:** Working on repositories you don't have locally, or testing changes on external projects

### Legacy Syntax (Deprecated)

For backward compatibility, the following flags still work but show deprecation warnings:

```bash
# Old way (still works)
aimux prompt --no-worktree --agents claude:2 "Your task"
aimux prompt --clone https://github.com/user/repo.git --agents claude:2 "Your task"

# New way (recommended)
aimux prompt --init-method=copy --agents claude:2 "Your task"
aimux prompt --init-method=clone --url=https://github.com/user/repo.git --agents claude:2 "Your task"
```

### Combining Methods

Note: When using `--init-method=clone`, the cloned repository is temporary. After cloning, aimux will create either a worktree or a copy from the cloned repository depending on your choice (worktree by default).

The clone method doesn't support combining with worktree/copy - it always creates a copy of the cloned repository since the source is temporary.

## Command Aliases

Short forms for faster workflow:

- `aimux p` → `aimux prompt`
- `aimux l` → `aimux ls`
- `aimux k` → `aimux kill`
- `aimux a` → `aimux auto`
- `aimux b` → `aimux broadcast`
- `aimux c` → `aimux checkpoint`
- `aimux r` → `aimux run`

Supports partial matches: `aimux pro`, `aimux prom`, `aimux prompt` all work!

## All Commands

1. **prompt (p)**: Create new agent sessions with prompts
   - `aimux prompt --agents claude:2 "task"`
   - `aimux prompt --no-worktree --agents aider:1 "task"`
   - `aimux prompt --clone https://github.com/user/repo.git --agents claude:2 "task"`

2. **ls (l)**: List active agent sessions
   - `aimux ls` - Show all sessions
   - `aimux ls -w` - Watch mode (live updates)

3. **kill (k)**: Terminate agent sessions
   - `aimux kill agent-name` - Kill specific agent
   - `aimux kill all` - Kill all agents

4. **auto (a)**: Auto-manage agent sessions
   - Watches for new prompts and spawns agents automatically
   - Concurrent monitoring with threading

5. **broadcast (b)**: Send messages to all agents
   - `aimux broadcast "Add error handling"`

6. **checkpoint (c)**: Save agent work with git commits
   - `aimux checkpoint agent-name "commit message"`

7. **run (r)**: Execute commands in all agent sessions
   - `aimux run "git status"`
   - `aimux run "npm test"`

8. **reset**: Delete all aimux data
   - Removes all worktrees, copies, and state files
   - Use with caution!

## Development & Testing

### Running Tests

```bash
# Using uv (recommended)
uv run pytest

# With coverage report
uv run pytest --cov=aimux --cov-report=term-missing

# Using pip
pip install -e ".[dev]"
pytest
```

### Test Suite Details

- **83 tests** covering all commands and features
- **57% overall coverage**, 100% on core modules (agents, config)
- Tests include:
  - Agent name uniqueness and generation
  - Config loading and validation
  - State persistence and recovery
  - CLI command routing and aliases
  - All 8 commands with various flag combinations
  - Git worktree operations
  - Directory copying with git exclusion
  - Repository cloning from URLs
  - Error handling and edge cases

### Code Quality

- ✅ Shell injection prevention (no `shell=True` with user input)
- ✅ Input validation (ports, paths, agent names)
- ✅ Automatic state file corruption recovery
- ✅ Type hints throughout codebase
- ✅ Comprehensive error messages
- ✅ Cross-platform path handling

## Project Structure

```
.
├── aimux/
│   ├── __init__.py
│   ├── cli.py              # CLI entry point & argument parsing
│   ├── agents.py           # Agent name generation (104 unique names)
│   ├── config.py           # YAML config loading
│   ├── state.py            # State persistence with error recovery
│   ├── cmd/
│   │   ├── prompt.py       # Agent creation (worktrees/copies/clone)
│   │   ├── ls.py           # List & watch sessions
│   │   ├── kill.py         # Terminate agents
│   │   ├── auto.py         # Auto-manage with threading
│   │   ├── broadcast.py    # Message all agents
│   │   ├── checkpoint.py   # Git commits
│   │   ├── run.py          # Execute in all sessions
│   │   └── reset.py        # Delete all data
├── tests/
│   ├── conftest.py         # Pytest fixtures
│   ├── test_agents.py
│   ├── test_config.py
│   ├── test_state.py
│   ├── test_cli.py
│   ├── test_prompt.py
│   ├── test_ls.py
│   └── ...
├── pyproject.toml          # Modern packaging config
├── uv.lock                 # Dependency lock file
├── README.md               # This file
├── README.go.md            # Original Go implementation docs
└── USAGE_EXAMPLES.md       # Extended usage examples
```

## Contributing

This is a faithful Python port of the original Go implementation with additional features:
- `--no-worktree` flag for directory copies
- `--clone` flag for cloning from URLs
- Modern Python packaging with uv support
- Comprehensive test suite

See [USAGE_EXAMPLES.md](USAGE_EXAMPLES.md) for more examples and use cases.

## License

BSD-3-Clause
