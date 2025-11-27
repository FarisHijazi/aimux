#!/usr/bin/env python3
"""Test script for project initialization methods."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def cleanup_test_data():
    """Clean up any test data from previous runs."""
    aimux_data = Path.home() / ".local" / "share" / "aimux"
    if aimux_data.exists():
        # Only remove test-related items
        for item in ["worktrees", "copies"]:
            test_dir = aimux_data / item
            if test_dir.exists():
                print(f"Cleaning up {test_dir}")
                for entry in test_dir.iterdir():
                    if "test" in entry.name.lower():
                        shutil.rmtree(entry, ignore_errors=True)


def test_worktree_method():
    """Test git worktree initialization method."""
    print("\n" + "=" * 60)
    print("TEST 1: Git Worktree Method (default)")
    print("=" * 60)

    # Test with explicit flag
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aimux",
            "prompt",
            "--init-method=worktree",
            "--agents=echo:1",
            "exit",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Check that it mentions worktree
    if "git worktrees" in result.stdout:
        print("✓ Worktree method selected correctly")
        return True
    else:
        print("✗ Worktree method not detected in output")
        return False


def test_copy_method():
    """Test hard copy initialization method."""
    print("\n" + "=" * 60)
    print("TEST 2: Hard Copy Method")
    print("=" * 60)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aimux",
            "prompt",
            "--init-method=copy",
            "--agents=echo:1",
            "exit",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Check that it mentions copy
    if "hard copy" in result.stdout:
        print("✓ Copy method selected correctly")
        return True
    else:
        print("✗ Copy method not detected in output")
        return False


def test_clone_method():
    """Test git clone initialization method."""
    print("\n" + "=" * 60)
    print("TEST 3: Git Clone Method")
    print("=" * 60)

    # Use a small public repository for testing
    test_repo = "https://github.com/octocat/Hello-World.git"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aimux",
            "prompt",
            "--init-method=clone",
            f"--url={test_repo}",
            "--agents=echo:1",
            "exit",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Check that it mentions cloning
    if "git clone" in result.stdout and test_repo in result.stdout:
        print("✓ Clone method selected correctly")
        return True
    else:
        print("✗ Clone method not detected in output")
        return False


def test_validation():
    """Test that validation works correctly."""
    print("\n" + "=" * 60)
    print("TEST 4: Validation (clone without URL)")
    print("=" * 60)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aimux",
            "prompt",
            "--init-method=clone",
            "test prompt",
        ],
        capture_output=True,
        text=True,
        timeout=5,
    )

    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Should fail with error message
    if "--url is required" in result.stderr:
        print("✓ Validation works correctly")
        return True
    else:
        print("✗ Validation did not catch missing URL")
        return False


def test_backward_compatibility():
    """Test backward compatibility with legacy flags."""
    print("\n" + "=" * 60)
    print("TEST 5: Backward Compatibility (--no-worktree)")
    print("=" * 60)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aimux",
            "prompt",
            "--no-worktree",
            "--agents=echo:1",
            "exit",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Should show deprecation warning and use copy method
    if "deprecated" in result.stdout.lower() and "hard copy" in result.stdout:
        print("✓ Backward compatibility maintained")
        return True
    else:
        print("✗ Backward compatibility issue detected")
        return False


def test_short_flags():
    """Test short flags -m and -u."""
    print("\n" + "=" * 60)
    print("TEST 6: Short Flags (-m and -u)")
    print("=" * 60)

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aimux",
            "prompt",
            "-m",
            "copy",
            "--agents=echo:1",
            "exit",
        ],
        capture_output=True,
        text=True,
        timeout=10,
    )

    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Check that short flag works
    if "hard copy" in result.stdout:
        print("✓ Short flag -m works correctly")
        return True
    else:
        print("✗ Short flag -m not working")
        return False


def test_url_implies_clone():
    """Test that --url implies clone method."""
    print("\n" + "=" * 60)
    print("TEST 7: URL Implies Clone")
    print("=" * 60)

    test_repo = "https://github.com/octocat/Hello-World.git"

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "aimux",
            "prompt",
            "-u",
            test_repo,
            "--agents=echo:1",
            "exit",
        ],
        capture_output=True,
        text=True,
        timeout=30,
    )

    print("STDOUT:", result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)

    # Check that clone is auto-detected
    if "git clone" in result.stdout and test_repo in result.stdout:
        print("✓ URL automatically implies clone method")
        return True
    else:
        print("✗ URL did not auto-detect clone method")
        return False


def test_config_default():
    """Test configurable default init method."""
    print("\n" + "=" * 60)
    print("TEST 8: Configurable Default Init Method")
    print("=" * 60)

    # Create a temporary config file
    config_content = """defaultInitMethod: copy
"""
    config_path = Path("test_aimux.yaml")
    config_path.write_text(config_content)

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "aimux",
                "prompt",
                "--config",
                "test_aimux.yaml",
                "--agents=echo:1",
                "exit",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )

        print("STDOUT:", result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)

        # Check that config default is used
        if "hard copy" in result.stdout:
            print("✓ Config default init method works correctly")
            return True
        else:
            print("✗ Config default init method not working")
            return False
    finally:
        # Clean up test config
        if config_path.exists():
            config_path.unlink()


def main():
    """Run all tests."""
    print("Project Initialization Methods - Test Suite")
    print("=" * 60)

    # Cleanup before tests
    cleanup_test_data()

    results = []

    # Run tests
    try:
        results.append(("Validation", test_validation()))
        results.append(("Worktree Method", test_worktree_method()))
        results.append(("Copy Method", test_copy_method()))
        results.append(("Clone Method", test_clone_method()))
        results.append(("Backward Compatibility", test_backward_compatibility()))
        results.append(("Short Flags", test_short_flags()))
        results.append(("URL Implies Clone", test_url_implies_clone()))
        results.append(("Config Default", test_config_default()))
    except Exception as e:
        print(f"\n✗ Test suite failed with error: {e}")
        import traceback

        traceback.print_exc()
        return 1

    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    for name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {name}")

    total_passed = sum(1 for _, passed in results if passed)
    total_tests = len(results)

    print(f"\nResults: {total_passed}/{total_tests} tests passed")

    # Cleanup after tests
    cleanup_test_data()

    return 0 if total_passed == total_tests else 1


if __name__ == "__main__":
    sys.exit(main())
