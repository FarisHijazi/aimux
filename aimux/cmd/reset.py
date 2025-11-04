"""Reset command - deletes all aimux data."""

import shutil
from pathlib import Path


def execute_reset():
    """Execute the reset command."""
    home_dir = Path.home()
    aimux_data_path = home_dir / ".local" / "share" / "aimux"

    if not aimux_data_path.exists():
        print("No aimux data found to reset")
        return

    # Ask for confirmation
    print(f"This will permanently delete all aimux data from {aimux_data_path}")
    response = input("Are you sure you want to continue? (y/N): ").strip().lower()

    if response not in ["y", "yes"]:
        print("Reset cancelled")
        return

    # Remove directory
    shutil.rmtree(aimux_data_path, ignore_errors=True)
    print(f"Successfully reset all aimux data from {aimux_data_path}")
