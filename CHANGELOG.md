# Changelog

All notable changes to the aimux Python implementation will be documented in this file.

## [0.2.0] - 2025-01-04

### Added

- **`--no-worktree` flag**: Option to use full directory copies instead of git worktrees
  - Copies entire directory recursively (excluding `.git`)
  - Initializes new git repo in copied directory
  - Useful for non-git projects or when full isolation is needed
  - Stored in `~/.local/share/aimux/copies/` instead of `worktrees/`

- **`--clone` flag**: Option to clone from repository URL before creating agents
  - Supports HTTPS and SSH URLs
  - Works with public and private repositories
  - Clones to temporary directory, then creates agents
  - Automatic cleanup of cloned repository after agent creation

- **7 new tests** for directory copying and repository cloning functionality
  - Test successful and failed cloning
  - Test recursive directory copying
  - Test `.git` exclusion in copies
  - Test integration with prompt command

### Changed

- `execute_prompt()` now accepts `no_worktree` and `clone_url` parameters
- CLI updated to support new flags with proper help text
- State management tracks both worktrees and copies

### Technical Details

- Uses `shutil.copytree()` with `.git` exclusion for directory copies
- Uses `subprocess.run(["git", "clone", ...])` for repository cloning
- Temporary directories created with `tempfile.mkdtemp()` for clones
- Cleanup handled in `try`/`finally` blocks to prevent leaks

## [0.1.0] - 2025-01-03

### Added

- Initial Python 3.11+ implementation of aimux
- All 8 core commands: prompt, ls, kill, auto, broadcast, checkpoint, run, reset
- Command aliases (p, l, k, a, b, c, r)
- Git worktree management
- Tmux session orchestration
- State persistence with error recovery
- YAML configuration support
- Threading for concurrent session watching
- Security improvements (shell injection prevention)
- Input validation (port ranges, agent specifications)
- 76 comprehensive tests with pytest
- Documentation and implementation notes

### Security

- Fixed shell injection vulnerabilities by using list-based subprocess arguments
- Validated port ranges (1-65535)
- Removed duplicate agent names

### Performance

- Added threading to auto-watcher for concurrent session monitoring
- Each agent session monitored in dedicated thread

### Reliability

- State file corruption handled with automatic backup
- Graceful error handling throughout
- Consistent error reporting to stderr
