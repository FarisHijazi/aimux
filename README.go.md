<a href="https://www.aimux.sh">
  <img src="https://trieve.b-cdn.net/www.aimux.sh_.png">
</a>
<p align="center">
  <a
    href="https://cdn.trieve.ai/aimux-whitepaper.pdf"
    target="_blank"
    rel="noopener noreferrer"
    >Whitepaper
  </a>
</p>

## Installation

```bash
go install github.com/devflowinc/aimux@latest
```

Make sure that your GOBIN is in your PATH.

```sh
export PATH="$PATH:$HOME/go/bin"
```

## Features

- 🤖 Run multiple AI coding agents in parallel
- 🌳 Automatic Git worktree management for isolated development
- 🖥️ Tmux session management for each agent
- 🚀 Automatic development server setup with port management
- 📊 Real-time monitoring of agent status and code changes
- 🔄 Automatic handling of agent prompts and confirmations
- 🎯 Easy checkpoint and merge of agent changes

## Prerequisites

- **Git**: For version control and worktree management
- **Tmux**: For terminal session management
- **Go**: For installing
- **Your AI tool of choice**: Such as `claude`, `codex`, etc.

## Configuration

### aimux.yaml

Create a `aimux.yaml` file in your project root to configure aimux:

```yaml
devCommand: cd astrobits && yarn && yarn dev --port $PORT
portRange: 3000-3010
```

#### Configuration Options

- **`devCommand`**: The command to start your development server. Use `$PORT` as a placeholder for the port number.
  - Example for Next.js: `npm install && npm run dev -- --port $PORT`
  - Example for Vite: `npm install && npm run dev -- --port $PORT`
  - Example for Django: `pip install -r requirements.txt && python manage.py runserver 0.0.0.0:$PORT`
- **`portRange`**: The range of ports aimux can use for development servers (format: `start-end`)

**Important**: The `devCommand` should include all necessary setup steps (like `npm install`, `pip install`, etc.) as each agent runs in an isolated worktree with its own dependencies.

## Basic Workflow

1. **Start agents with a task:**

   ```bash
   aimux prompt --agents claude:3,codex:2 "Implement a REST API for user management with authentication"
   ```

2. **Run aimux auto**

   aimux auto automatically presses Enter to confirm all tool calls

   ```
   aimux auto
   ```

3. **Monitor agent progress:**

   ```bash
   aimux ls -w  # Watch mode
   ```

4. **Send additional instructions:**

   ```bash
   aimux broadcast "Make sure to add input validation"
   ```

5. **Merge completed work:**
   ```bash
   aimux checkpoint funny-elephant "feat: add user management API"
   ```

## Commands

### `aimux prompt` (alias: `aimux p`)

Creates new agent sessions with the specified prompt.

```bash
aimux prompt --agents claude:2,codex:1 "Build a todo app with React"
```

**Options:**

- `--agents`: Specify agents and counts in format `agent:count[,agent:count...]`
  - Use `random` as agent name for random agent names
  - Example: `--agents claude:2,random:3`

### `aimux ls` (alias: `aimux l`)

Lists all active agent sessions with their status.

```bash
aimux ls       # List active sessions
aimux ls -w    # Watch mode - refreshes every second
```

```
AGENT    MODEL  STATUS    DIFF  ADDR                     PROMPT
brian    codex  ready  +0/-0  http://localhost:3003  make a component that looks similar to @astrobits/src/components/Button/ that creates a Tooltip in the same style. Ensure that you include a reference to it and examples on the main page.
gregory  codex  ready  +0/-0  http://localhost:3001  make a component that `
```

### `aimux auto` (alias: `aimux a`)

Monitors all agent sessions and automatically handles prompts.

```bash
aimux auto
```

**Features:**

- Auto-presses Enter for trust prompts
- Handles continuation confirmations
- Runs in the background until interrupted (Ctrl+C)

### `aimux kill` (alias: `aimux k`)

Terminates agent sessions and cleans up resources.

```bash
aimux kill agent-name    # Kill specific agent
aimux kill all          # Kill all agents
```

### `aimux run` (alias: `aimux r`)

Executes a command in all active agent sessions.

```bash
aimux run "git status"              # Run in all agents
aimux run --delete "npm test"       # Run and delete the window after
```

**Options:**

- `--delete`: Remove the tmux window after running the command

### `aimux broadcast` (alias: `aimux b`)

Sends a message to all active agent sessions.

```bash
aimux broadcast "Please add error handling to all API calls"
```

### `aimux checkpoint` (alias: `aimux c`)

Makes a commit and rebases changes from an agent's worktree into your current branch.

```bash
aimux checkpoint agent-name "feat: implement user authentication"
```

### `aimux reset`

Removes all aimux data and configuration.

```bash
aimux reset
```

**Warning**: This deletes all data in `~/.local/share/aimux`

### Advanced Usage

**Running different AI tools:**

```bash
aimux prompt --agents=claude:2,aider:2,cursor:1 "Refactor the authentication system"
```

**Using random agent names:**

```bash
aimux prompt --agents=random:5 "Fix all TypeScript errors"
```

**Running tests across all agents:**

```bash
aimux run "npm test"
```
