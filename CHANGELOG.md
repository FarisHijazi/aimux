# Changelog

All notable changes to the aimux Python implementation will be documented in this file.

## [0.3.0] - 2025-11-07

### Added

- **`--init-method` / `-m` parameter**: Explicit, user-friendly way to choose project initialization method
  - Three options: `worktree` (default), `copy`, `clone`
  - Short flag `-m` for frequent use
  - Clear help text explaining each method
  - Automatic validation: `--url` required when using `clone` method
  - User-friendly output showing which method is being used

- **`--url` / `-u` parameter**: Specify repository URL
  - Short flag `-u` for convenient use
  - **Auto-detection**: Automatically implies `--init-method=clone` when provided
  - Works with HTTPS and SSH URLs
  - Just use `-u URL` - no need to specify `-m clone` explicitly!

- **Configurable default initialization method**:
  - Set `defaultInitMethod: copy|worktree|clone` in `aimux.yaml`
  - Applies when no explicit method specified
  - Validation with fallback to `worktree` for invalid values

- **Smart precedence system** for determining init method:
  1. Explicit `--init-method` flag (highest priority)
  2. Legacy flags (`--no-worktree` or `--clone`)
  3. Auto-detection from `--url` flag
  4. Config file `defaultInitMethod`
  5. Default to `worktree` (lowest priority)

- **Comprehensive test suite** (`test_init_methods.py`):
  - Tests all three initialization methods
  - Validates error handling and validation logic
  - Tests backward compatibility with legacy flags
  - Tests short flags functionality
  - Tests URL auto-detection
  - Tests config default behavior
  - All 8 tests passing

### Changed

- `execute_prompt()` enhanced with new `init_method` and `url` parameters
- Improved user feedback with initialization method descriptions
- Better error messages for invalid configurations

### Deprecated

- `--no-worktree` flag (use `--init-method=copy` instead)
- `--clone URL` flag (use `--init-method=clone --url=URL` instead)

Both deprecated flags still work and show deprecation warnings to guide users to the new syntax.

### Documentation

- Added `CLAUDE.md` documenting the session changes
- Added usage examples for all three initialization methods
- Added migration guide for users of deprecated flags

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
