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

- `uzi p` - prompt
- `uzi l` - ls
- `uzi k` - kill
- `uzi a` - auto
- `uzi b` - broadcast
- `uzi c` - checkpoint
- `uzi r` - run

## License

BSD-3-Clause
