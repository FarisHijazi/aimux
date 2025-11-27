# CLAUDE.md - Session Documentation

This file documents changes made by Claude during development sessions.

## Session: 2025-11-07 - Project Initialization Methods

### Summary

Added a new `--init-method` parameter to provide an explicit and user-friendly way to choose between project initialization methods. This enhancement improves usability while maintaining backward compatibility with existing flags.

**UPDATE**: Enhanced with short flags, auto-detection, and configurable defaults for even better user experience.

### Changes Made

#### 1. New CLI Parameters (`aimux/cli.py`)

Added `--init-method` / `-m` parameter with three options:
- `worktree`: Git worktrees (linked to current repository) - **default**
- `copy`: Hard copy of project directory
- `clone`: Git clone from URL

Added `--url` / `-u` parameter to specify repository URL.
- **Auto-detection**: Providing `-u URL` automatically implies `--init-method=clone`
- No need to specify both `-m clone` and `-u URL` - just `-u URL` is enough!

Marked legacy flags as deprecated:
- `--no-worktree` → Use `--init-method=copy` instead
- `--clone URL` → Use `--init-method=clone --url=URL` instead

#### 2. Configurable Default (`aimux/config.py`)

Added `defaultInitMethod` configuration option to `aimux.yaml`:
- Users can set their preferred default initialization method
- Valid values: `worktree`, `copy`, or `clone`
- Falls back to `worktree` if not specified or invalid

#### 3. Enhanced Logic (`aimux/cmd/prompt.py`)

Updated `execute_prompt()` function to:
- Accept new `init_method` and `url` parameters
- **Auto-detect clone**: If `--url` is provided without `--init-method`, automatically use `clone`
- **Config default**: Read `defaultInitMethod` from config file if no method specified
- Handle backward compatibility with legacy flags
- Validate that `--url` is provided when using `--init-method=clone`
- Display clear message showing which initialization method is being used
- Show deprecation warnings when legacy flags are used

Priority order for determining init method:
1. Explicit `--init-method` flag (highest priority)
2. Legacy flags (`--no-worktree` or `--clone`)
3. Auto-detection from `--url` flag
4. Config file `defaultInitMethod`
5. Default to `worktree` (lowest priority)

#### 4. Comprehensive Testing (`test_init_methods.py`)

Created test suite that validates:
- ✅ Git worktree initialization
- ✅ Hard copy initialization
- ✅ Git clone from URL initialization
- ✅ Validation (clone requires URL)
- ✅ Backward compatibility with legacy flags
- ✅ Short flags (`-m`, `-u`)
- ✅ URL auto-detection (implies clone)
- ✅ Config default init method

All tests pass (8/8).

### Usage Examples

#### Method 1: Git Worktree (Default)
```bash
# Explicit (long form)
aimux prompt --init-method=worktree "add feature X"

# Explicit (short form)
aimux prompt -m worktree "add feature X"

# Implicit (default behavior)
aimux prompt "add feature X"
```

#### Method 2: Hard Copy
```bash
# Long form
aimux prompt --init-method=copy "add feature Y"

# Short form
aimux prompt -m copy "add feature Y"
```

#### Method 3: Clone from URL
```bash
# Short form with auto-detection (RECOMMENDED)
aimux prompt -u https://github.com/user/repo.git "add feature Z"

# Explicit long form
aimux prompt --init-method=clone --url=https://github.com/user/repo.git "add feature Z"

# Short form explicit
aimux prompt -m clone -u https://github.com/user/repo.git "add feature Z"
```

#### Config File Default
```yaml
# In aimux.yaml
defaultInitMethod: copy
```

```bash
# Now this uses 'copy' instead of 'worktree'
aimux prompt "add feature"
```

#### Legacy Compatibility
```bash
# These still work but show deprecation warnings
aimux prompt --no-worktree "add feature"
aimux prompt --clone https://github.com/user/repo.git "add feature"
```

### Technical Details

**Key Features:**
- **Short flags**: `-m` for `--init-method`, `-u` for `--url` (frequently used)
- **Auto-detection**: `--url` automatically implies `clone` method
- **Configurable default**: Set `defaultInitMethod` in `aimux.yaml`
- **Smart precedence**: Explicit flag > Legacy flag > URL detection > Config > Default
- Backward compatible with existing `--no-worktree` and `--clone` flags
- Proper validation: `--url` required when using `--init-method=clone`
- User-friendly error messages and informational output
- Consistent behavior across all initialization methods

**Files Modified:**
- `aimux/cli.py` - Added short flags and updated help text
- `aimux/config.py` - Added `default_init_method` configuration
- `aimux/cmd/prompt.py` - Enhanced initialization logic with auto-detection

**Files Created:**
- `test_init_methods.py` - Comprehensive test suite (8 tests)
- `CLAUDE.md` - This documentation file

### Testing

Run the test suite:
```bash
python test_init_methods.py
```

Expected output: 8/8 tests passed

### Migration Guide

**For users currently using `--no-worktree`:**
```bash
# Old (deprecated)
aimux prompt --no-worktree "prompt text"

# New (recommended)
aimux prompt --init-method=copy "prompt text"
```

**For users currently using `--clone`:**
```bash
# Old (deprecated)
aimux prompt --clone https://github.com/user/repo.git "prompt text"

# New (recommended)
aimux prompt --init-method=clone --url=https://github.com/user/repo.git "prompt text"
```

### Benefits

1. **Clarity**: Explicit parameter name makes it clear what's being configured
2. **Discoverability**: Shows up in `--help` with clear descriptions
3. **Validation**: Prevents invalid combinations (e.g., clone without URL)
4. **Backward Compatible**: Existing scripts continue to work
5. **User Friendly**: Clear messages about which method is being used
6. **Testable**: Comprehensive test coverage ensures reliability

### Future Considerations

- Consider adding interactive mode to prompt user for initialization method
- Add configuration file support for default initialization method
- Consider adding more initialization methods (e.g., `sparse-checkout`, `shallow-clone`)
