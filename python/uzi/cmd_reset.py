"""Reset command - deletes all uzi data."""

import shutil
from pathlib import Path


def execute_reset():
    """Execute the reset command."""
    home_dir = Path.home()
    uzi_data_path = home_dir / ".local" / "share" / "uzi"

    if not uzi_data_path.exists():
        print("No uzi data found to reset")
        return

    # Ask for confirmation
    print(f"This will permanently delete all uzi data from {uzi_data_path}")
    response = input("Are you sure you want to continue? (y/N): ").strip().lower()

    if response not in ['y', 'yes']:
        print("Reset cancelled")
        return

    # Remove directory
    shutil.rmtree(uzi_data_path, ignore_errors=True)
    print(f"Successfully reset all uzi data from {uzi_data_path}")
