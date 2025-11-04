# aimux Usage Examples

Comprehensive examples demonstrating all features of the Python implementation.

## Table of Contents

1. [Basic Usage](#basic-usage)
2. [Using Directory Copies](#using-directory-copies)
3. [Cloning from URLs](#cloning-from-urls)
4. [Combined Options](#combined-options)
5. [Advanced Workflows](#advanced-workflows)

## Basic Usage

### Default Mode: Git Worktrees

The default mode uses git worktrees for efficient, space-saving isolated environments:

```bash
# In your project directory
cd /path/to/your/project

# Create 2 claude agents
aimux prompt --agents claude:2 "Add user authentication with JWT"

# List active agents
aimux ls

# Output shows:
# AGENT    MODEL   STATUS    DIFF      ADDR                     PROMPT
# john     claude  ready     +0/-0     http://localhost:3000    Add user authentication with JWT
# emily    claude  ready     +0/-0     http://localhost:3001    Add user authentication with JWT
```

**How it works:**
- Creates git worktrees in `~/.local/share/aimux/worktrees/`
- Each agent gets its own branch
- Changes tracked by git
- Minimal disk space (shared .git objects)

## Using Directory Copies

### When to Use `--no-worktree`

Use `--no-worktree` when you need:
- Full independence from the main repository
- To work with non-git directories
- Maximum isolation between agents
- Simpler mental model (just copies)

### Examples

#### Example 1: Non-Git Project

```bash
cd /path/to/non-git-project

# This would fail with default worktree mode
# But works with --no-worktree
aimux prompt --no-worktree --agents claude:2 "Refactor the main module"
```

#### Example 2: Maximum Isolation

```bash
# Each agent gets a completely independent copy
aimux prompt --no-worktree --agents claude:3 "Experiment with different architectures"

# Agents can make conflicting changes without issues
# No shared git history or objects
```

#### Example 3: Learning/Teaching

```bash
# Easier to understand for beginners
# No need to understand git worktrees
aimux prompt --no-worktree --agents aider:1 "Add a todo feature"
```

**Storage location:** `~/.local/share/aimux/copies/`

**What gets copied:**
- All files and directories (recursively)
- Symlinks (preserved)
- Permissions
- **Excludes:** `.git` directory

**Post-copy:**
- New git repo initialized
- All files added and committed
- Ready for agent to make changes

## Cloning from URLs

### When to Use `--clone`

Use `--clone` when you want to:
- Experiment with external projects
- Work on repos you don't have locally
- Test agents on different codebases
- CI/CD automation

### Examples

#### Example 1: Public Repository

```bash
# Clone and create agents in one command
aimux prompt --clone https://github.com/facebook/react.git --agents claude:2 "Add TypeScript support to hooks"
```

**What happens:**
1. Clones repo to `/tmp/aimux_clone_XXXXX/`
2. Creates worktrees/copies from cloned repo
3. Spawns agents in their environments
4. Cleans up temporary clone directory

#### Example 2: Private Repository (HTTPS)

```bash
# Uses your git credentials (cached or credential helper)
aimux prompt --clone https://github.com/mycompany/private-repo.git --agents claude:2 "Fix authentication bug"
```

#### Example 3: Private Repository (SSH)

```bash
# Uses your SSH keys
aimux prompt --clone git@github.com:mycompany/private-repo.git --agents codex:2 "Optimize database queries"
```

#### Example 4: Specific Branch

```bash
# Clone the repo, then specify branch in prompt
aimux prompt --clone https://github.com/user/repo.git --agents claude:1 "Start from the develop branch and add feature"
```

**Note:** The clone creates worktrees by default. For full copies, combine with `--no-worktree`.

## Combined Options

### Maximum Isolation: Clone + No-Worktree

Perfect for experimentation without any git complexity:

```bash
aimux prompt \
  --clone https://github.com/user/repo.git \
  --no-worktree \
  --agents claude:3 \
  "Try three different approaches to solve the performance issue"
```

**Result:**
- 3 completely independent copies
- Cloned from remote repo
- No shared git history
- No worktree management
- Each agent completely isolated

### Efficient Git Tracking: Clone + Worktrees (Default)

Best for maintaining git history while experimenting:

```bash
aimux prompt \
  --clone https://github.com/user/repo.git \
  --agents claude:2,codex:1 \
  "Implement the new API endpoint"
```

**Result:**
- 3 agents (2 claude, 1 codex)
- All share git objects (space efficient)
- Changes tracked in branches
- Easy to merge successful approaches

## Advanced Workflows

### Workflow 1: Parallel Experimentation

```bash
# Create multiple agents with different AI models
aimux prompt --agents claude:2,codex:2,aider:1 "Implement OAuth2 authentication"

# Monitor their progress
aimux ls -w  # Watch mode, refreshes every second

# Auto-handle prompts
aimux auto

# Send additional instructions
aimux broadcast "Make sure to add input validation"

# When one finishes successfully
aimux checkpoint john "feat: add OAuth2 authentication"
```

### Workflow 2: External Repo Testing

```bash
# Test agents on a popular open source project
aimux prompt \
  --clone https://github.com/nodejs/node.git \
  --agents claude:1 \
  "Analyze the event loop implementation and suggest optimizations"

# List sessions
aimux ls

# Kill when done
aimux kill all
```

### Workflow 3: Non-Git Experimentation

```bash
cd /path/to/legacy-code  # No git

# Create isolated copies for experimentation
aimux prompt --no-worktree --agents claude:3 "Modernize the codebase to use ES6+"

# Each agent works independently
# No git knowledge required
```

### Workflow 4: CI/CD Integration

```bash
#!/bin/bash
# ci-test-agents.sh

# Clone repo and run agents for testing
aimux prompt \
  --clone "$CI_REPOSITORY_URL" \
  --no-worktree \
  --agents "claude:3" \
  "Review code for security vulnerabilities"

# Wait for completion (monitor with polling)
while [ "$(aimux ls | grep -c running)" -gt 0 ]; do
  sleep 10
done

# Collect results
aimux ls > agent-results.txt
```

### Workflow 5: Multi-Repo Development

```bash
# Work on multiple repos simultaneously
aimux prompt --clone https://github.com/user/frontend.git --agents claude:1 "Update API client"
aimux prompt --clone https://github.com/user/backend.git --agents claude:1 "Add new endpoint"
aimux prompt --clone https://github.com/user/mobile.git --agents codex:1 "Update mobile app"

# List all active sessions across repos
aimux ls
```

## Comparison Table

| Feature | Default (Worktrees) | `--no-worktree` | `--clone` | `--clone --no-worktree` |
|---------|-------------------|-----------------|-----------|------------------------|
| **Requires Git** | Yes | No | Yes | No (after clone) |
| **Disk Usage** | Low (shared objects) | High (full copies) | Low | High |
| **Git Tracking** | Yes (branches) | Yes (new repo) | Yes (branches) | Yes (new repo) |
| **Isolation** | Medium | Maximum | Medium | Maximum |
| **Speed** | Fast | Medium | Medium (clone time) | Slow (clone + copy) |
| **Use Case** | Local development | Non-git/Max isolation | External repos | External + isolation |

## Tips and Best Practices

### Disk Space Management

```bash
# Check disk usage
du -sh ~/.local/share/aimux/

# Clean up old copies/worktrees
aimux kill all
rm -rf ~/.local/share/aimux/copies/*  # Be careful!
```

### Credential Management

For `--clone` with private repos:

```bash
# Cache credentials (15 minutes)
git config --global credential.helper cache

# Or use SSH keys (recommended)
ssh-add ~/.ssh/id_rsa
```

### Performance Optimization

```bash
# For large repos, use shallow clone
git clone --depth=1 <url>  # Then use aimux normally

# Or use sparse checkout
git clone --filter=blob:none <url>
```

### Monitoring Multiple Sessions

```bash
# Terminal 1: Watch sessions
aimux ls -w

# Terminal 2: Auto-handle prompts
aimux auto

# Terminal 3: Monitor system resources
htop
```

## Troubleshooting

### Issue: Clone Fails with Authentication

```bash
# Solution: Check credentials
git ls-remote <url>  # Test git access first

# For HTTPS, cache credentials
git config --global credential.helper store

# For SSH, add key
ssh-add -l  # List keys
ssh-add ~/.ssh/id_rsa  # Add if needed
```

### Issue: Directory Copy is Slow

```bash
# Solution: Use worktrees instead
aimux prompt --agents claude:2 "Task"  # Default, much faster

# Or copy only what's needed
rsync -av --exclude='node_modules' source/ dest/
```

### Issue: Running Out of Disk Space

```bash
# Check usage
du -sh ~/.local/share/aimux/*/

# Clean up
aimux kill all
aimux reset  # Removes ALL aimux data (careful!)
```

## Summary

The Python implementation of aimux provides flexible options for agent orchestration:

- **Default mode**: Efficient git worktrees for local development
- **`--no-worktree`**: Full directory copies for maximum isolation
- **`--clone`**: Work with external repositories seamlessly
- **Combined**: Maximum flexibility for any workflow

Choose the option that best fits your use case!
