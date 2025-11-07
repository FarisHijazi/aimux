# CLAUDE.md - Session Documentation

This file documents changes made by Claude during development sessions.

## Session: 2025-11-07 - Project Initialization Methods

### Summary

Added a new `--init-method` parameter to provide an explicit and user-friendly way to choose between project initialization methods. This enhancement improves usability while maintaining backward compatibility with existing flags.

### Changes Made

#### 1. New CLI Parameter (`aimux/cli.py`)

Added `--init-method` parameter with three options:
- `worktree`: Git worktrees (linked to current repository) - **default**
- `copy`: Hard copy of project directory
- `clone`: Git clone from URL

Added `--url` parameter to specify repository URL when using `--init-method=clone`.

Marked legacy flags as deprecated:
- `--no-worktree` → Use `--init-method=copy` instead
- `--clone URL` → Use `--init-method=clone --url=URL` instead

#### 2. Enhanced Logic (`aimux/cmd/prompt.py`)

Updated `execute_prompt()` function to:
- Accept new `init_method` and `url` parameters
- Handle backward compatibility with legacy flags
- Validate that `--url` is provided when using `--init-method=clone`
- Display clear message showing which initialization method is being used
- Show deprecation warnings when legacy flags are used

#### 3. Comprehensive Testing (`test_init_methods.py`)

Created test suite that validates:
- ✅ Git worktree initialization
- ✅ Hard copy initialization
- ✅ Git clone from URL initialization
- ✅ Validation (clone requires URL)
- ✅ Backward compatibility with legacy flags

All tests pass (5/5).

### Usage Examples

#### Method 1: Git Worktree (Default)
```bash
# Explicit
aimux prompt --init-method=worktree "add feature X"

# Implicit (default behavior)
aimux prompt "add feature X"
```

#### Method 2: Hard Copy
```bash
aimux prompt --init-method=copy "add feature Y"
```

#### Method 3: Clone from URL
```bash
aimux prompt --init-method=clone --url=https://github.com/user/repo.git "add feature Z"
```

#### Legacy Compatibility
```bash
# These still work but show deprecation warnings
aimux prompt --no-worktree "add feature"
aimux prompt --clone https://github.com/user/repo.git "add feature"
```

### Technical Details

**Key Features:**
- Clear, explicit choice mechanism via `--init-method` parameter
- Backward compatible with existing `--no-worktree` and `--clone` flags
- Proper validation: `--url` required when using `--init-method=clone`
- User-friendly error messages and informational output
- Consistent behavior across all initialization methods

**Files Modified:**
- `aimux/cli.py` - Added new CLI parameters and routing
- `aimux/cmd/prompt.py` - Enhanced initialization logic

**Files Created:**
- `test_init_methods.py` - Comprehensive test suite
- `CLAUDE.md` - This documentation file

### Testing

Run the test suite:
```bash
python test_init_methods.py
```

Expected output: 5/5 tests passed

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
