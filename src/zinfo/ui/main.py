"""Main entry point for zinfo GUI application.

This module provides the main entry point for launching the zinfo GUI application.
Uses NullUI for headless/CLI-only usage.
"""

import logging
import sys
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def _select_cache_path_from_args(argv: list[str]) -> tuple[list[str], Optional[Path]]:
    """Parse argv to extract cache path from positional args.

    Returns:
        (remaining_argv, cache_path)
    """
    cache_path: Optional[Path] = None
    remaining = list(argv)

    # Determine cache_path if any positional arg remains (first non-flag)
    positional = [a for a in remaining[1:] if not a.startswith("-")]  # skip argv[0]
    if positional:
        try:
            cache_path = Path(positional[0])
        except Exception:
            cache_path = None

    return remaining, cache_path


def _instantiate_gui():
    """Instantiate the NullUI app class for headless usage."""
    from .null_ui import NullUI
    return NullUI()


def run_gui(cache_path: Optional[Path] = None) -> None:
    """Run the zinfo GUI application.

    Args:
        cache_path: Optional path to the cache database. If None, uses default.
    """
    # Configure logging once
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    logger.info("Starting zinfo GUI application")

    # Create and start the GUI application
    gui_app = _instantiate_gui()
    gui_app.startup()

    # Initialize cache if path provided
    if cache_path and gui_app.zinfo_app:
        gui_app.zinfo_app.initialize_cache(cache_path)

    # Show the main window (enters main loop)
    gui_app.show_main_window()


def main():
    """Main entry point for the GUI application."""
    _, cache_path = _select_cache_path_from_args(sys.argv)

    # Run the GUI
    run_gui(cache_path)


if __name__ == "__main__":
    main()
