# Uzi Test Suite

Comprehensive test suite for the Uzi Python implementation using pytest.

## Test Coverage

The test suite includes **76 tests** covering:

- **Agent name generation** (9 tests)
- **Configuration loading** (8 tests)
- **State management** (13 tests)
- **CLI routing and aliases** (19 tests)
- **Prompt command** (16 tests)
- **List command** (9 tests)
- **Other commands** (2 tests)

**Overall coverage: 57%** (680 statements, 293 missed)

### Coverage by Module

| Module | Coverage | Notes |
|--------|----------|-------|
| `agents.py` | 100% | Fully tested |
| `config.py` | 100% | Fully tested |
| `cli.py` | 96% | Nearly complete |
| `state.py` | 81% | Core functionality tested |
| `prompt.py` | 87% | Core functionality tested |
| `ls.py` | 77% | Core functionality tested |
| `auto.py` | 19% | Hard to test without real tmux |
| `kill.py` | 13% | Requires git/tmux integration |
| `checkpoint.py` | 8% | Requires git integration |
| Other commands | 10-23% | Require tmux/git integration |

## Running Tests

### Run all tests
```bash
pytest tests/
```

### Run with verbose output
```bash
pytest tests/ -v
```

### Run specific test file
```bash
pytest tests/test_agents.py -v
```

### Run specific test
```bash
pytest tests/test_agents.py::TestAgentNames::test_agent_names_count -v
```

### Run with coverage
```bash
pytest tests/ --cov=uzi --cov-report=term-missing
```

### Run with coverage HTML report
```bash
pytest tests/ --cov=uzi --cov-report=html
open htmlcov/index.html
```

## Test Structure

```
tests/
├── __init__.py              # Package marker
├── conftest.py              # Pytest fixtures and configuration
├── test_agents.py           # Agent name generation tests
├── test_config.py           # Configuration loading tests
├── test_state.py            # State management tests
├── test_cli.py              # CLI and command routing tests
├── test_prompt.py       # Prompt command tests
├── test_ls.py           # List command tests
└── README.md                # This file
```

## Test Fixtures

The test suite includes several useful fixtures (defined in `conftest.py`):

- **`temp_dir`** - Temporary directory for test files
- **`mock_git_repo`** - Mock git repository with initial commit
- **`mock_state_dir`** - Mock uzi state directory
- **`mock_config_file`** - Mock uzi.yaml configuration file
- **`sample_state_data`** - Sample state data for testing

## Test Categories

### Unit Tests

Test individual functions and components in isolation:
- Agent name generation
- Configuration parsing
- State file operations
- Port availability checking
- Agent specification parsing

### Integration Tests

Test interactions between components:
- Command execution flow
- State persistence
- Configuration loading
- CLI command routing

### Mock-Heavy Tests

Some commands require extensive mocking due to external dependencies:
- Git operations (worktree, branch, commit)
- Tmux operations (session, window, pane)
- Subprocess execution

## What's Not Tested

Some functionality is difficult to test without real system integration:

1. **Tmux Session Management**
   - Creating/killing tmux sessions
   - Sending keys to panes
   - Capturing pane content

2. **Git Worktree Operations**
   - Creating worktrees
   - Branch management
   - Rebasing operations

3. **Auto-Watcher Threading**
   - Real-time session monitoring
   - Concurrent prompt handling

4. **Port Binding**
   - Actual network port availability
   - Dev server startup

## Development

### Adding New Tests

1. Create test file: `tests/test_<module>.py`
2. Import module: `from uzi import <module>`
3. Create test class: `class Test<Feature>`
4. Write test methods: `def test_<behavior>(self)`

Example:
```python
from uzi import mymodule

class TestMyFeature:
    def test_basic_functionality(self):
        result = mymodule.my_function("input")
        assert result == "expected"
```

### Test Naming Convention

- **File**: `test_<module>.py`
- **Class**: `Test<Feature>` (describes what's being tested)
- **Method**: `test_<behavior>` (describes expected behavior)

### Using Fixtures

```python
def test_with_temp_dir(temp_dir):
    """Test that uses temporary directory."""
    test_file = temp_dir / "test.txt"
    test_file.write_text("content")
    assert test_file.exists()
```

## Continuous Integration

To run tests in CI/CD:

```bash
# Install dependencies
pip install -e .[dev]

# Run tests with coverage
pytest tests/ --cov=uzi --cov-report=xml --cov-report=term

# Check coverage threshold (optional)
pytest tests/ --cov=uzi --cov-fail-under=50
```

## Future Improvements

Potential additions to the test suite:

1. **Integration Tests**
   - Real git repository testing
   - Real tmux session testing (in CI environment)

2. **End-to-End Tests**
   - Full workflow testing
   - Multi-agent scenarios

3. **Performance Tests**
   - Large agent counts
   - State file performance
   - Port allocation speed

4. **Property-Based Tests**
   - Using hypothesis for fuzz testing
   - Random input generation

5. **Snapshot Tests**
   - CLI output verification
   - State file format verification

## Contributing

When adding new features:

1. Write tests first (TDD approach)
2. Ensure existing tests pass
3. Aim for >80% coverage on new code
4. Add integration tests where possible
5. Update this README if needed

## License

BSD-3-Clause (same as main project)
