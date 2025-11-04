# Uzi - Python Implementation

A Python 3.11+ implementation of Uzi, an AI coding agent orchestration tool that helps you manage multiple AI coding agents working on the same codebase in parallel, each in isolated environments with tmux sessions.

## Quick Start

Try it instantly without installation:

```bash
uvx --from git+https://github.com/FarisHijazi/aimux uzi --help
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
uvx --from git+https://github.com/FarisHijazi/aimux uzi --help

# Create an alias for convenience
alias uzi='uvx --from git+https://github.com/FarisHijazi/aimux uzi'
```

### Using uvx (local development)

If you've cloned the repo:

```bash
uvx --from . uzi --help
```

### Using uv (for local development with venv)

```bash
uv sync
# Then either activate: source .venv/bin/activate
# Or prefix commands: uv run uzi --help
```

This creates a virtual environment with pinned dependencies via uv.lock.

### Using pip (development install)

```bash
pip install -e .
```

### Using pip (from PyPI)

```bash
pip install uzi  # Coming soon
```

## Prerequisites

- Python 3.11+
- Git (for version control and worktree management)
- Tmux (for terminal session management)
- Your AI tool of choice (such as `claude`, `codex`, etc.)
- [uv](https://docs.astral.sh/uv/) (optional but recommended for faster dependency management)

## Configuration

Create a `uzi.yaml` file in your project root:

```yaml
devCommand: cd myproject && npm install && npm run dev -- --port $PORT
portRange: 3000-3010
```

## Basic Usage

> **Note:**
> - If using uvx from GitHub: `uvx --from git+https://github.com/FarisHijazi/aimux uzi <command>`
> - If installed with `uv sync`: activate venv or prefix with `uv run uzi <command>`
> - If using uvx locally: `uvx --from . uzi <command>`
> - If installed with pip: just use `uzi <command>`

```bash
# Create agent sessions (uses git worktrees by default)
uzi prompt --agents claude:2 "Implement a REST API"

# Create agent sessions with directory copies instead of worktrees
uzi prompt --no-worktree --agents claude:2 "Implement a REST API"

# Create agent sessions by cloning from a repository URL
uzi prompt --clone https://github.com/user/repo.git --agents claude:2 "Implement a REST API"

# Combine both: clone and use copies
uzi prompt --clone https://github.com/user/repo.git --no-worktree --agents claude:2 "Implement a REST API"

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

## Advanced Options

### Working Without Git Worktrees

By default, uzi uses git worktrees to create isolated development environments. If you prefer to work with full directory copies instead:

```bash
uzi prompt --no-worktree --agents claude:2 "Your task"
```

**Benefits of `--no-worktree`:**
- Works with non-git directories
- Full independence from main repository
- No git worktree limitations
- Easier to understand for beginners

**Tradeoffs:**
- Uses more disk space (full copies)
- Changes aren't tracked with git branches
- Slower initial setup (full copy vs. worktree)

### Cloning from Repository URLs

You can create agent sessions from any git repository without cloning it first:

```bash
uzi prompt --clone https://github.com/user/repo.git --agents claude:2 "Your task"
```

**Use cases:**
- Quick experimentation with external projects
- Working on repositories you don't have locally
- Parallel development on different repos
- CI/CD integration

**Supports:**
- HTTPS URLs: `https://github.com/user/repo.git`
- SSH URLs: `git@github.com:user/repo.git`
- Private repositories (uses your git credentials)

### Combining Options

```bash
# Clone and use copies (maximum isolation)
uzi prompt --clone https://github.com/user/repo.git --no-worktree --agents claude:3 "Task"

# Clone with worktrees (efficient git tracking)
uzi prompt --clone https://github.com/user/repo.git --agents claude:3 "Task"
```

## Command Aliases

Short forms for faster workflow:

- `uzi p` → `uzi prompt`
- `uzi l` → `uzi ls`
- `uzi k` → `uzi kill`
- `uzi a` → `uzi auto`
- `uzi b` → `uzi broadcast`
- `uzi c` → `uzi checkpoint`
- `uzi r` → `uzi run`

Supports partial matches: `uzi pro`, `uzi prom`, `uzi prompt` all work!

## All Commands

1. **prompt (p)**: Create new agent sessions with prompts
   - `uzi prompt --agents claude:2 "task"`
   - `uzi prompt --no-worktree --agents aider:1 "task"`
   - `uzi prompt --clone https://github.com/user/repo.git --agents claude:2 "task"`

2. **ls (l)**: List active agent sessions
   - `uzi ls` - Show all sessions
   - `uzi ls -w` - Watch mode (live updates)

3. **kill (k)**: Terminate agent sessions
   - `uzi kill agent-name` - Kill specific agent
   - `uzi kill all` - Kill all agents

4. **auto (a)**: Auto-manage agent sessions
   - Watches for new prompts and spawns agents automatically
   - Concurrent monitoring with threading

5. **broadcast (b)**: Send messages to all agents
   - `uzi broadcast "Add error handling"`

6. **checkpoint (c)**: Save agent work with git commits
   - `uzi checkpoint agent-name "commit message"`

7. **run (r)**: Execute commands in all agent sessions
   - `uzi run "git status"`
   - `uzi run "npm test"`

8. **reset**: Delete all uzi data
   - Removes all worktrees, copies, and state files
   - Use with caution!

## Development & Testing

### Running Tests

```bash
# Using uv (recommended)
uv run pytest

# With coverage report
uv run pytest --cov=uzi --cov-report=term-missing

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
├── uzi/
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
